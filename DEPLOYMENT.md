# 🚀 Hunter Pro CRM - دليل النشر الشامل

## جدول المحتويات

1. [النشر السريع](#النشر-السريع)
2. [المتطلبات](#المتطلبات)
3. [طرق النشر](#طرق-النشر)
4. [الإعداد والتكوين](#الإعداد-والتكوين)
5. [الأمان والإنتاج](#الأمان-والإنتاج)
6. [المراقبة والصيانة](#المراقبة-والصيانة)

---

## النشر السريع

### Docker Compose (الطريقة الموصى بها)

```bash
# 1. استنساخ المشروع
git clone https://github.com/yourusername/hunter-pro-ultimate.git
cd hunter-pro-ultimate

# 2. نسخ ملف البيئة
cp .env.example .env

# 3. تحديث المتغيرات الحساسة
nano .env  # أضف API Keys والمفاتيح السرية

# 4. بناء وتشغيل
docker-compose up -d

# 5. فحص الحالة
docker-compose ps
docker-compose logs -f app
```

**الوصول:**
- Dashboard: http://localhost:5000
- API Docs: http://localhost:5000/docs
- Grafana: http://localhost:3000

---

## المتطلبات

### الحد الأدنى (Development)
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB
- OS: Linux, macOS, Windows (WSL2)

### الموصى به (Production)
- CPU: 4+ cores
- RAM: 8GB+
- Disk: 50GB+ SSD
- OS: Ubuntu 22.04 LTS

### البرمجيات
- Docker 24.0+
- Docker Compose 2.20+
- Python 3.11+ (للنشر بدون Docker)
- PostgreSQL 15+ (للنشر بدون Docker)
- Redis 7+ (للنشر بدون Docker)

---

## طرق النشر

### 1️⃣ Docker Compose (محلي/تطوير)

#### الخطوات:
```bash
# البناء
docker-compose build

# التشغيل
docker-compose up -d

# إيقاف
docker-compose down

# إعادة التشغيل
docker-compose restart app

# عرض السجلات
docker-compose logs -f app
```

#### الخدمات المشمولة:
- ✅ FastAPI Application
- ✅ PostgreSQL Database
- ✅ Redis Cache
- ✅ Ollama (AI Local)
- ✅ Celery Workers
- ✅ Nginx (Optional)
- ✅ Prometheus + Grafana (Optional)

---

### 2️⃣ Kubernetes (إنتاج/مؤسسات)

#### المتطلبات:
- Kubernetes 1.27+
- kubectl
- Helm 3.12+

#### الخطوات:

```bash
# 1. إنشاء Namespace
kubectl create namespace hunter-pro

# 2. إنشاء Secrets
kubectl create secret generic hunter-secrets \
  --from-env-file=.env \
  -n hunter-pro

# 3. نشر PostgreSQL
kubectl apply -f deployments/kubernetes/postgres.yaml -n hunter-pro

# 4. نشر Redis
kubectl apply -f deployments/kubernetes/redis.yaml -n hunter-pro

# 5. نشر التطبيق
kubectl apply -f deployments/kubernetes/app-deployment.yaml -n hunter-pro
kubectl apply -f deployments/kubernetes/app-service.yaml -n hunter-pro

# 6. نشر Ingress
kubectl apply -f deployments/kubernetes/ingress.yaml -n hunter-pro

# 7. فحص الحالة
kubectl get pods -n hunter-pro
kubectl get svc -n hunter-pro
kubectl logs -f deployment/hunter-app -n hunter-pro
```

#### Auto-scaling:
```yaml
# deployments/kubernetes/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: hunter-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: hunter-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

---

### 3️⃣ السحابة - AWS

#### EC2 + Docker:
```bash
# 1. إطلاق EC2 Instance (t3.medium+)
# 2. تثبيت Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo usermod -a -G docker ec2-user

# 3. تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 4. استنساخ ونشر
git clone https://github.com/yourusername/hunter-pro-ultimate.git
cd hunter-pro-ultimate
cp .env.example .env
nano .env  # Configure
docker-compose up -d
```

#### ECS (Elastic Container Service):
```bash
# 1. بناء ونشر Image
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker build -t hunter-pro .
docker tag hunter-pro:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/hunter-pro:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/hunter-pro:latest

# 2. إنشاء Task Definition
aws ecs register-task-definition --cli-input-json file://ecs-task-def.json

# 3. إنشاء Service
aws ecs create-service \
  --cluster hunter-cluster \
  --service-name hunter-service \
  --task-definition hunter-task \
  --desired-count 2 \
  --launch-type FARGATE
```

#### RDS + ElastiCache:
```bash
# 1. إنشاء RDS PostgreSQL
aws rds create-db-instance \
  --db-instance-identifier hunter-db \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username admin \
  --master-user-password YOUR_PASSWORD \
  --allocated-storage 100

# 2. إنشاء ElastiCache Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id hunter-cache \
  --cache-node-type cache.t3.medium \
  --engine redis \
  --num-cache-nodes 1
```

---

### 4️⃣ السحابة - Google Cloud Platform

#### Cloud Run (Serverless):
```bash
# 1. بناء Image
gcloud builds submit --tag gcr.io/PROJECT_ID/hunter-pro

# 2. النشر
gcloud run deploy hunter-pro \
  --image gcr.io/PROJECT_ID/hunter-pro \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...,REDIS_URL=redis://..."

# 3. الحصول على URL
gcloud run services describe hunter-pro --format='value(status.url)'
```

#### GKE (Google Kubernetes Engine):
```bash
# 1. إنشاء Cluster
gcloud container clusters create hunter-cluster \
  --num-nodes=3 \
  --machine-type=n1-standard-2 \
  --region=us-central1

# 2. الاتصال بـ Cluster
gcloud container clusters get-credentials hunter-cluster

# 3. النشر
kubectl apply -f deployments/kubernetes/
```

---

### 5️⃣ السحابة - Microsoft Azure

#### Azure Container Instances:
```bash
# 1. إنشاء Resource Group
az group create --name hunter-rg --location eastus

# 2. إنشاء Container Registry
az acr create --resource-group hunter-rg --name hunterregistry --sku Basic

# 3. بناء ونشر Image
az acr build --registry hunterregistry --image hunter-pro:latest .

# 4. النشر
az container create \
  --resource-group hunter-rg \
  --name hunter-app \
  --image hunterregistry.azurecr.io/hunter-pro:latest \
  --cpu 2 \
  --memory 4 \
  --ports 5000
```

---

## الإعداد والتكوين

### ملف .env الأساسي

```bash
# ==================== APPLICATION ====================
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=5000

# ==================== SECURITY ====================
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_SECRET=your-jwt-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION=3600

# ==================== DATABASE ====================
DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/hunter_pro
DATABASE_NAME=hunter_pro
DATABASE_USER=postgres
DATABASE_PASSWORD=your-postgres-password

# ==================== REDIS ====================
REDIS_URL=redis://:your-redis-password@redis:6379/0
REDIS_PASSWORD=your-redis-password

# ==================== AI PROVIDERS ====================
# OpenAI
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo

# Claude
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-3-5-sonnet-20240620

# Google Gemini
GOOGLE_API_KEY=AIza...
GOOGLE_MODEL=gemini-1.5-flash

# Groq
GROQ_API_KEY=gsk_...
GROQ_MODEL=llama3-70b-8192

# Ollama (Local)
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3:8b

# Default Provider
DEFAULT_AI_PROVIDER=openai

# ==================== CORS ====================
CORS_ORIGINS=*  # Production: https://yourdomain.com,https://www.yourdomain.com

# ==================== MONITORING ====================
GRAFANA_PASSWORD=your-grafana-password
```

---

## الأمان والإنتاج

### 1. HTTPS/SSL

#### باستخدام Let's Encrypt + Certbot:
```bash
# 1. تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# 2. الحصول على شهادة
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 3. التجديد التلقائي
sudo certbot renew --dry-run
```

#### Nginx Configuration:
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://app:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### 3. النسخ الاحتياطي التلقائي

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Database backup
docker exec hunter_postgres pg_dump -U postgres hunter_pro > $BACKUP_DIR/db_$DATE.sql

# Redis backup
docker exec hunter_redis redis-cli --rdb /data/dump_$DATE.rdb

# Compress
tar -czf $BACKUP_DIR/backup_$DATE.tar.gz $BACKUP_DIR/db_$DATE.sql $BACKUP_DIR/dump_$DATE.rdb

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/backup_$DATE.tar.gz s3://your-backup-bucket/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "backup_*.tar.gz" -mtime +7 -delete
```

---

## المراقبة والصيانة

### فحص الصحة

```bash
# Application
curl http://localhost:5000/health

# Database
docker exec hunter_postgres pg_isready

# Redis
docker exec hunter_redis redis-cli ping
```

### السجلات

```bash
# Application logs
docker-compose logs -f app

# Database logs
docker-compose logs -f postgres

# All services
docker-compose logs -f
```

### التحديثات

```bash
# Pull latest changes
git pull origin main

# Rebuild
docker-compose build

# Deploy with zero-downtime
docker-compose up -d --no-deps --build app
```

---

## استكشاف الأخطاء

### مشكلة: التطبيق لا يبدأ

```bash
# Check logs
docker-compose logs app

# Check database connection
docker-compose exec app python -c "from app.core.database import engine; print('DB OK')"

# Restart services
docker-compose restart
```

### مشكلة: بطء الأداء

```bash
# Check resource usage
docker stats

# Check database queries
docker-compose logs postgres | grep "duration:"

# Clear Redis cache
docker-compose exec redis redis-cli FLUSHALL
```

### مشكلة: AI لا يعمل

```bash
# Check AI service
docker-compose exec app python -c "from app.services.ai_service import ai_service; print(ai_service.get_available_providers())"

# Test provider
curl -X POST http://localhost:5000/api/ai/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Test", "provider": "ollama"}'
```

---

## الدعم

- 📧 Email: support@hunterpro.com
- 📚 Documentation: https://docs.hunterpro.com
- 💬 Discord: https://discord.gg/hunterpro
- 🐛 Issues: https://github.com/yourusername/hunter-pro-ultimate/issues

---

**مبنى بواسطة Hunter Pro Team | v7.0.0 | 2024**
