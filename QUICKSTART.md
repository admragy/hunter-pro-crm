# 🚀 Quick Start Guide - Hunter Pro CRM Ultimate Enterprise

## ⚡ 5-Minute Setup

Get Hunter Pro running in 5 minutes!

---

## Option 1: Docker (Recommended - Fastest)

```bash
# 1. Download and extract
wget https://github.com/yourusername/hunter-pro/releases/download/v7.0.0/hunter-pro-v7.0.0.tar.gz
tar -xzf hunter-pro-v7.0.0.tar.gz
cd hunter-pro-ultimate-enterprise

# 2. Start all services with one command
docker-compose up -d

# 3. Open in browser
open http://localhost:5000/dashboard

# Default login:
# Email: admin@hunterpro.com
# Password: ChangeThisPassword123!
```

**That's it! ✅ You're ready to go!**

---

## Option 2: Python (Development)

```bash
# 1. Clone or download
git clone https://github.com/yourusername/hunter-pro.git
cd hunter-pro

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env

# 5. Run application
python main.py

# 6. Open browser
open http://localhost:5000/dashboard
```

---

## ⚙️ Essential Configuration

### Minimum Required (Free Tier)

Edit `.env` file:

```env
# Application
SECRET_KEY="generate-a-random-32-char-secret-here"
DATABASE_URL="sqlite:///./hunter_pro.db"

# AI - Choose ONE (all have free tiers)
GOOGLE_API_KEY="your-gemini-key"     # Best free option
# OR
GROQ_API_KEY="your-groq-key"         # Fastest free option
# OR
OLLAMA_BASE_URL="http://localhost:11434"  # Local, no key needed
```

### Get Free API Keys

1. **Google Gemini (Best Free)**: https://aistudio.google.com/
   - Free tier: 60 requests/minute
   - Click "Get API Key"
   
2. **Groq (Fastest Free)**: https://console.groq.com/
   - Free tier: Very generous
   - Sign up and create API key
   
3. **Ollama (Local AI)**: https://ollama.ai/
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Download model
   ollama pull llama3:8b
   
   # Run
   ollama serve
   ```

---

## 🧪 Test Your Setup

```bash
# Check health
curl http://localhost:5000/health

# Check info
curl http://localhost:5000/info

# Expected response:
# {"status": "healthy", "version": "7.0.0", ...}
```

---

## 📱 Access Points

Once running:

- **Dashboard**: http://localhost:5000/dashboard
- **API Docs**: http://localhost:5000/docs
- **API Alternative**: http://localhost:5000/redoc
- **Health Check**: http://localhost:5000/health
- **WebSocket**: ws://localhost:5000/ws

---

## 🎯 First Steps

### 1. Login
```
Email: admin@hunterpro.com
Password: ChangeThisPassword123!
```

**⚠️ IMPORTANT**: Change password immediately!

### 2. Add Your First Customer
```bash
curl -X POST http://localhost:5000/api/customers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Acme Corp",
    "email": "contact@acme.com",
    "phone": "+1234567890"
  }'
```

### 3. Try AI Chat
```bash
curl -X POST http://localhost:5000/api/ai/chat \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze my customer database",
    "provider": "auto"
  }'
```

---

## 🔧 Common Issues & Solutions

### Issue: "Cannot connect to database"
```bash
# Solution: Check DATABASE_URL in .env
# For development, use SQLite:
DATABASE_URL="sqlite:///./hunter_pro.db"
```

### Issue: "Redis connection failed"
```bash
# Solution 1: Disable Redis (optional)
CACHE_ENABLED=false

# Solution 2: Install Redis
# Mac:
brew install redis && brew services start redis
# Linux:
sudo apt install redis-server && sudo systemctl start redis
# Windows:
# Download from: https://redis.io/download
```

### Issue: "AI provider error"
```bash
# Solution: Check your API key
# Test with curl:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_KEY"

# Or use free Ollama:
ollama serve
# Then set in .env:
DEFAULT_AI_PROVIDER="ollama"
```

### Issue: "Port 5000 already in use"
```bash
# Solution: Change port in .env or command line
PORT=8000 python main.py
# Or
python main.py --port 8000
```

---

## 🐳 Docker Troubleshooting

```bash
# View logs
docker-compose logs -f app

# Restart services
docker-compose restart

# Stop all
docker-compose down

# Clean start
docker-compose down -v  # Remove volumes
docker-compose up -d --build
```

---

## 📚 Next Steps

### Learn More:
1. Read [README.md](README.md) for full documentation
2. Check [API docs](http://localhost:5000/docs) for API reference
3. Review [DELIVERY.md](DELIVERY.md) for development guide

### Configure Features:
1. Setup WhatsApp integration (see README)
2. Connect Facebook Ads (see README)
3. Configure email service (see README)
4. Enable analytics (see README)

### Customize:
1. Change theme colors in `static/css/`
2. Modify dashboard in `templates/dashboard.html`
3. Add custom AI prompts in `app/services/ai_service.py`

---

## 🆘 Get Help

- 📖 **Documentation**: http://localhost:5000/docs
- 📧 **Email**: support@hunterpro.com
- 💬 **Discord**: https://discord.gg/hunterpro
- 🐛 **Issues**: https://github.com/yourusername/hunter-pro/issues

---

## ✅ Success Checklist

- [ ] Application running at http://localhost:5000
- [ ] Can access dashboard
- [ ] Can login with default credentials
- [ ] Health check returns "healthy"
- [ ] At least one AI provider configured
- [ ] Database connected
- [ ] Changed default admin password

**Congratulations! 🎉 You're all set!**

---

## 🚀 Production Deployment

Ready for production? Check these guides:

- [AWS Deployment Guide](docs/deployment/aws.md)
- [Google Cloud Deployment](docs/deployment/gcp.md)
- [DigitalOcean Deployment](docs/deployment/digitalocean.md)
- [Kubernetes Deployment](docs/deployment/kubernetes.md)

---

**Need help?** Don't hesitate to reach out!

Happy CRM-ing! 🎊