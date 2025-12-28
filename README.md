# Hunter Pro CRM Ultimate Enterprise v7.0.0

![Hunter Pro CRM](https://img.shields.io/badge/version-7.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![FastAPI](https://img.shields.io/badge/fastapi-0.109.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> 🚀 **Enterprise-Grade CRM System with AI, WhatsApp, Facebook Ads & More**

---

## 🎯 Overview

Hunter Pro CRM is a comprehensive, production-ready Customer Relationship Management system built with modern technologies and enterprise-grade features.

### ⭐ Key Features

- 🤖 **Multi-Provider AI Integration** (6 providers)
- 💬 **WhatsApp Integration** (6 operational modes)
- 📢 **Facebook Ads Management** (10 Unicorn strategies)
- 🔐 **Advanced Authentication** (JWT, 2FA, OAuth2)
- 📊 **Advanced Analytics & Reports** (PDF/Excel)
- ⚡ **Real-time Chat** (WebSocket)
- 📧 **Email Integration** (SMTP)
- 🔗 **Webhook System**
- 🌍 **Multi-language Support** (Arabic RTL + 5)
- 📱 **PWA Ready**

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (recommended)

### Installation

```bash
# Clone repository
git clone https://github.com/admragy/hunter-pro-ultimate.git
cd hunter-pro-ultimate

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Install dependencies
pip install -r requirements.txt

# Run with Docker (recommended)
docker-compose up -d

# OR run directly
python main.py
```

### Access

- 🌐 **Dashboard**: http://localhost:5000
- 📖 **API Docs**: http://localhost:5000/docs
- 📊 **ReDoc**: http://localhost:5000/redoc
- 🏥 **Health Check**: http://localhost:5000/health

---

## 📦 Project Structure

```
hunter-pro-ultimate-enterprise/
├── app/
│   ├── api/routes/          # API endpoints (70+)
│   ├── core/                # Core configurations
│   ├── models/              # Database models
│   └── services/            # Business logic (12 services)
├── templates/               # HTML templates
├── static/                  # JS, CSS, assets
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies (150+)
├── docker-compose.yml       # Docker services (11)
└── .env.example            # Environment template
```

---

## 🔐 Authentication

### Supported Methods

- ✅ JWT (Access + Refresh Tokens)
- ✅ 2FA (Two-Factor Authentication)
- ✅ OAuth2 (Google, Azure AD)
- ✅ API Keys
- ✅ Session Management

### Example Usage

```python
# Register
POST /api/auth/register
{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "name": "John Doe"
}

# Login
POST /api/auth/login
{
    "username": "user@example.com",
    "password": "SecurePass123!"
}

# Enable 2FA
POST /api/auth/2fa/enable
Headers: Authorization: Bearer {access_token}
```

---

## 🤖 AI Integration

### Supported Providers

| Provider | Model | Use Case |
|----------|-------|----------|
| OpenAI | GPT-4 Turbo | Advanced reasoning |
| Anthropic | Claude 3.5 Sonnet | Long context |
| Google | Gemini Pro | Multimodal |
| Groq | Llama 3 70B | Fast inference |
| Ollama | Local models | Privacy-first |
| Custom | Your models | Full control |

### Example Usage

```python
# Generate text
POST /api/ai/generate
{
    "prompt": "Analyze customer sentiment",
    "provider": "openai",
    "temperature": 0.7
}

# Analyze sentiment
POST /api/ai/sentiment
{
    "text": "I love this product!"
}
```

---

## 💬 WhatsApp Integration

### 6 Operational Modes

1. **Selenium** - WebDriver automation
2. **Twilio** - Twilio WhatsApp API
3. **Cloud API** - WhatsApp Business Cloud API
4. **Webhook** - Receive messages
5. **Local** - Local development
6. **Bulk** - Mass messaging

### Example Usage

```python
# Send message
POST /api/whatsapp/send
{
    "phone": "+1234567890",
    "message": "Hello from Hunter Pro!"
}

# Send template
POST /api/whatsapp/send-template
{
    "phone": "+1234567890",
    "template_name": "welcome",
    "language": "en"
}
```

---

## 📢 Facebook Ads

### 10 Unicorn Strategies

1. Lookalike Audiences
2. Retargeting
3. Engagement
4. Conversion
5. Video Views
6. Traffic
7. App Installs
8. Lead Generation
9. Messages
10. Catalog Sales

### Example Usage

```python
# Create campaign
POST /api/facebook-ads/campaigns
{
    "name": "Summer Sale 2024",
    "objective": "OUTCOME_SALES",
    "status": "PAUSED"
}

# Get insights
GET /api/facebook-ads/campaigns/{id}/insights?date_preset=last_7d
```

---

## 📊 Reports & Analytics

### Supported Formats

- ✅ PDF Reports (Charts + Tables)
- ✅ Excel Multi-sheet
- ✅ Dashboard Reports
- ✅ Custom Branding

### Example Usage

```python
# Generate PDF
POST /api/reports/pdf
{
    "title": "Monthly Report",
    "data": {...},
    "charts": [...]
}

# Download dashboard report
GET /api/reports/dashboard/pdf?period=last_30_days
```

---

## ⚡ Real-time Features

### WebSocket Chat

```javascript
// Connect to WebSocket
const ws = new WebSocket('ws://localhost:5000/ws/1');

// Send message
ws.send(JSON.stringify({
    type: 'chat',
    recipient_id: 2,
    message: 'Hello!'
}));

// Receive message
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Application
ENVIRONMENT=production
DEBUG=false
HOST=0.0.0.0
PORT=5000

# Security
SECRET_KEY=your-super-secret-key
JWT_SECRET=your-jwt-secret

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
REDIS_URL=redis://:password@host:6379/0

# AI Providers (Optional)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
GROQ_API_KEY=gsk_...

# WhatsApp (Optional)
WHATSAPP_MODE=cloud_api
WHATSAPP_CLOUD_API_TOKEN=...

# Facebook Ads (Optional)
FACEBOOK_ACCESS_TOKEN=...
FACEBOOK_AD_ACCOUNT_ID=...

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

---

## 🚀 Deployment

### Docker Compose (Recommended)

```bash
docker-compose up -d
```

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/admragy/hunter-pro-ultimate)

### Vercel

```bash
vercel --prod
```

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on:
- AWS (EC2, ECS, RDS)
- Google Cloud (Cloud Run, GKE)
- Azure (ACI, AKS)
- DigitalOcean
- Heroku

---

## 📚 API Documentation

### Endpoints Summary

| Category | Endpoints | Description |
|----------|-----------|-------------|
| Authentication | 10 | JWT, 2FA, OAuth2 |
| CRM | 15 | Customers, Deals |
| AI | 7 | Multi-provider AI |
| WhatsApp | 5 | 6 operational modes |
| Facebook Ads | 4 | 10 strategies |
| Reports | 3 | PDF, Excel |
| Email | 2 | SMTP integration |
| Webhooks | 3 | Event system |
| WebSocket | 1 | Real-time chat |
| **Total** | **70+** | Full API coverage |

Full API documentation available at: `/docs` (Swagger) or `/redoc` (ReDoc)

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app tests/

# Specific test
pytest tests/test_api.py
```

---

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Deployment Guide](DEPLOYMENT.md)
- [API Reference](https://localhost:5000/docs)
- [Architecture](docs/architecture.md)

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

---

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- OpenAI, Anthropic, Google for AI capabilities
- All open-source contributors

---

## 📞 Support

- 📧 **Email**: support@hunterpro.com
- 💬 **Discord**: https://discord.gg/hunterpro
- 📚 **Documentation**: https://docs.hunterpro.com
- 🐛 **Issues**: [GitHub Issues](https://github.com/admragy/hunter-pro-ultimate/issues)

---

## 📊 Stats

![GitHub stars](https://img.shields.io/github/stars/admragy/hunter-pro-ultimate?style=social)
![GitHub forks](https://img.shields.io/github/forks/admragy/hunter-pro-ultimate?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/admragy/hunter-pro-ultimate?style=social)

---

**Built with ❤️ by Hunter Pro Team**

**Version:** 7.0.0 Ultimate Edition  
**Status:** Production Ready ✅  
**Last Updated:** December 2024

---

## ⭐ Star History

If you find this project useful, please consider giving it a star!

[![Star History Chart](https://api.star-history.com/svg?repos=admragy/hunter-pro-ultimate&type=Date)](https://star-history.com/#admragy/hunter-pro-ultimate&Date)
