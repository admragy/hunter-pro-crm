"""
Hunter Pro CRM Ultimate Enterprise - Database Management
Version: 7.0.0
Advanced database setup with async support and connection pooling
"""

from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, DeclarativeBase
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy import event, MetaData
from contextlib import asynccontextmanager
import logging

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

# ========== Database Base ==========
# Naming convention for constraints
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

class Base(DeclarativeBase):
    """Base class for all database models"""
    metadata = metadata


# ========== Database Engine ==========
def get_database_url() -> str:
    """Get database URL from settings"""
    return settings.DATABASE_URL


def create_engine() -> AsyncEngine:
    """Create async database engine with connection pooling"""
    
    database_url = get_database_url()
    
    # Configuration based on database type
    engine_args = {
        "echo": settings.DB_ECHO,
        "future": True,
    }
    
    # SQLite specific configuration
    if "sqlite" in database_url:
        engine_args["connect_args"] = {
            "check_same_thread": False,
            "timeout": 30,
        }
        engine_args["poolclass"] = NullPool
        logger.info("🗄️ Using SQLite database")
    
    # PostgreSQL specific configuration
    elif "postgresql" in database_url:
        engine_args["pool_size"] = settings.DB_POOL_SIZE
        engine_args["max_overflow"] = settings.DB_MAX_OVERFLOW
        engine_args["pool_timeout"] = settings.DB_POOL_TIMEOUT
        engine_args["pool_pre_ping"] = True
        engine_args["poolclass"] = QueuePool
        logger.info("🗄️ Using PostgreSQL database")
    
    # MySQL specific configuration
    elif "mysql" in database_url:
        engine_args["pool_size"] = settings.DB_POOL_SIZE
        engine_args["max_overflow"] = settings.DB_MAX_OVERFLOW
        engine_args["pool_timeout"] = settings.DB_POOL_TIMEOUT
        engine_args["pool_pre_ping"] = True
        engine_args["pool_recycle"] = 3600  # Recycle connections every hour
        engine_args["poolclass"] = QueuePool
        logger.info("🗄️ Using MySQL database")
    
    engine = create_async_engine(database_url, **engine_args)
    
    # Event listeners for SQLite
    if "sqlite" in database_url:
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=-64000")  # 64MB
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
    
    return engine


# Global engine instance
engine: Optional[AsyncEngine] = None


def get_engine() -> AsyncEngine:
    """Get or create global engine instance"""
    global engine
    if engine is None:
        engine = create_engine()
    return engine


# ========== Session Management ==========
# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=get_engine(),
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Context manager for database session
    Usage:
        async with get_db_context() as db:
            # do something with db
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database context error: {e}")
            raise
        finally:
            await session.close()


# ========== Database Initialization ==========
async def init_db():
    """Initialize database - create all tables"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import (
                user,
                customer,
                deal,
                message,
                campaign,
                activity,
                task,
                note,
                file,
            )
            
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database tables created successfully")
        
        # Create default admin user if not exists
        await create_default_admin()
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


async def drop_db():
    """Drop all database tables (USE WITH CAUTION!)"""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("⚠️ All database tables dropped!")
    except Exception as e:
        logger.error(f"❌ Error dropping database: {e}")
        raise


async def reset_db():
    """Reset database - drop and recreate all tables"""
    logger.warning("⚠️ Resetting database...")
    await drop_db()
    await init_db()
    logger.info("✅ Database reset completed")


# ========== Database Health Check ==========
async def check_db_connection() -> bool:
    """Check if database connection is healthy"""
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        logger.info("✅ Database connection is healthy")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def get_db_info() -> dict:
    """Get database information"""
    try:
        engine = get_engine()
        return {
            "url": str(engine.url).split("@")[-1] if "@" in str(engine.url) else str(engine.url),
            "driver": engine.dialect.name,
            "pool_size": engine.pool.size() if hasattr(engine, "pool") else None,
            "checked_out_connections": engine.pool.checkedout() if hasattr(engine, "pool") else None,
            "status": "connected" if await check_db_connection() else "disconnected",
        }
    except Exception as e:
        logger.error(f"Error getting database info: {e}")
        return {"status": "error", "error": str(e)}


# ========== Default Data Creation ==========
async def create_default_admin():
    """Create default admin user if not exists"""
    try:
        from app.models.user import User
        from app.core.security import get_password_hash
        
        async with get_db_context() as db:
            # Check if admin exists
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.email == settings.ADMIN_EMAIL)
            )
            admin = result.scalar_one_or_none()
            
            if not admin:
                admin = User(
                    email=settings.ADMIN_EMAIL,
                    username="admin",
                    hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                    first_name=settings.ADMIN_FIRST_NAME,
                    last_name=settings.ADMIN_LAST_NAME,
                    is_active=True,
                    is_superuser=True,
                    is_verified=True,
                )
                db.add(admin)
                await db.commit()
                logger.info(f"✅ Default admin user created: {settings.ADMIN_EMAIL}")
            else:
                logger.info("ℹ️ Admin user already exists")
    
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")


# ========== Database Migration Helpers ==========
async def run_migrations():
    """Run database migrations using Alembic"""
    try:
        from alembic.config import Config
        from alembic import command
        
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        logger.info("✅ Database migrations completed")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        raise


# ========== Connection Pool Management ==========
async def dispose_engine():
    """Dispose database engine and close all connections"""
    global engine
    if engine is not None:
        await engine.dispose()
        engine = None
        logger.info("✅ Database engine disposed")


async def get_pool_status() -> dict:
    """Get database connection pool status"""
    try:
        engine = get_engine()
        if hasattr(engine, "pool"):
            pool = engine.pool
            return {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "total": pool.size() + pool.overflow(),
            }
        else:
            return {"message": "No pool available (using NullPool)"}
    except Exception as e:
        logger.error(f"Error getting pool status: {e}")
        return {"error": str(e)}


# ========== Startup and Shutdown Events ==========
async def startup_db():
    """Database startup event"""
    logger.info("🚀 Initializing database...")
    
    # Check connection
    is_connected = await check_db_connection()
    if not is_connected:
        raise Exception("Cannot connect to database")
    
    # Initialize database
    await init_db()
    
    # Log database info
    db_info = await get_db_info()
    logger.info(f"📊 Database Info: {db_info}")
    
    logger.info("✅ Database startup completed")


async def shutdown_db():
    """Database shutdown event"""
    logger.info("🛑 Shutting down database...")
    await dispose_engine()
    logger.info("✅ Database shutdown completed")


# ========== Transaction Context Manager ==========
@asynccontextmanager
async def transaction():
    """
    Transaction context manager
    Usage:
        async with transaction() as db:
            # operations will be committed automatically
            # or rolled back on exception
    """
    async with get_db_context() as db:
        try:
            yield db
            await db.commit()
        except Exception:
            await db.rollback()
            raise


# ========== Bulk Operations ==========
async def bulk_insert(model_class, objects: list):
    """Bulk insert objects"""
    async with get_db_context() as db:
        db.add_all([model_class(**obj) for obj in objects])
        await db.commit()
        logger.info(f"✅ Bulk inserted {len(objects)} {model_class.__name__} objects")


async def bulk_update(model_class, objects: list):
    """Bulk update objects"""
    async with get_db_context() as db:
        await db.execute(model_class.__table__.update(), objects)
        await db.commit()
        logger.info(f"✅ Bulk updated {len(objects)} {model_class.__name__} objects")


# ========== Database Statistics ==========
async def get_table_counts() -> dict:
    """Get row count for all tables"""
    from app.models import user, customer, deal, message, campaign
    
    tables = {
        "users": user.User,
        "customers": customer.Customer,
        "deals": deal.Deal,
        "messages": message.Message,
        "campaigns": campaign.Campaign,
    }
    
    counts = {}
    async with get_db_context() as db:
        from sqlalchemy import select, func
        for name, model in tables.items():
            result = await db.execute(select(func.count()).select_from(model))
            counts[name] = result.scalar()
    
    return counts


if __name__ == "__main__":
    import asyncio
    
    async def test():
        """Test database functions"""
        print("🧪 Testing database...")
        
        # Check connection
        is_connected = await check_db_connection()
        print(f"Connected: {is_connected}")
        
        # Get database info
        db_info = await get_db_info()
        print(f"Database Info: {db_info}")
        
        # Get pool status
        pool_status = await get_pool_status()
        print(f"Pool Status: {pool_status}")
        
        print("✅ Database tests completed")
    
    asyncio.run(test())