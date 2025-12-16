# 🚀 Quick Start Guide - ShopeeFlashBot SaaS

## What is this?

ShopeeFlashBot has been transformed into a **complete SaaS platform** that allows multiple users to automate Shopee flash sale purchases through a web API.

## 🎯 Quick Setup (3 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and change SECRET_KEY
```

### 3. Start Server
```bash
python -m saas.app
```

The API will be available at **http://localhost:8000**

### 4. Access Documentation
Open **http://localhost:8000/docs** in your browser for interactive API documentation.

## 📱 Try It Out

### Create a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","username":"testuser","password":"password123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

Save the `access_token` from the response!

### Create a Bot Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Flash Sale",
    "url": "https://shopee.co.id/product-url",
    "target_time": "00:00:00",
    "config": {
      "product_option": "Red",
      "payment_method": "ShopeePay"
    }
  }'
```

### Run the Task
```bash
curl -X POST http://localhost:8000/api/v1/tasks/1/run \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Subscription Tiers

| Feature | Free | Basic | Premium |
|---------|------|-------|---------|
| **Price** | $0 | $9.99/mo | $29.99/mo |
| **Bots** | 1 | 3 | 10 |
| **Schedules** | 5 | 20 | 100 |
| **Support** | Email | Priority | 24/7 |

## 📚 Full Documentation

- **[SAAS_ARCHITECTURE.md](SAAS_ARCHITECTURE.md)** - Complete technical documentation
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[SAAS_README_ID.md](SAAS_README_ID.md)** - Panduan dalam Bahasa Indonesia
- **[COMPARISON.md](COMPARISON.md)** - Original vs SaaS comparison
- **[SAAS_TRANSFORMATION_SUMMARY.md](SAAS_TRANSFORMATION_SUMMARY.md)** - Executive summary

## 💻 Using the Python Client

```python
from examples.api_client import ShopeeFlashBotClient

# Create client
client = ShopeeFlashBotClient()

# Register and login
client.register("user@example.com", "username", "password")
client.login("user@example.com", "password")

# Create and run task
task = client.create_task(
    name="Flash Sale",
    url="https://shopee.co.id/product",
    target_time="00:00:00",
    config={"payment_method": "ShopeePay"}
)

client.run_task(task['id'])
```

## 🔧 Troubleshooting

### Can't start server?
- Make sure Python 3.9+ is installed
- Check if port 8000 is available
- Verify all dependencies are installed

### Chrome/ChromeDriver issues?
- Install Google Chrome browser
- The `undetected-chromedriver` package manages the driver automatically

### Need help?
- Check the [full documentation](SAAS_ARCHITECTURE.md)
- Open an issue on GitHub
- Contact: muflihul.aufa@gmail.com

## 🎉 What's Next?

1. **Deploy to Production** - See [DEPLOYMENT.md](DEPLOYMENT.md)
2. **Add Payment Gateway** - Integrate Stripe or Midtrans
3. **Build Frontend** - Create a React/Vue dashboard
4. **Add Features** - Webhooks, analytics, notifications
5. **Launch Your Business** - Start accepting customers!

## ⚠️ Important Notes

- This platform is for educational purposes
- Automated purchasing may violate Shopee's TOS
- Users are responsible for compliance
- Always respect rate limits and fair use

## 📞 Support

- Email: muflihul.aufa@gmail.com
- Instagram: [@mufrajwaa](https://instagram.com/mufrajwaa)
- GitHub: [@bruhismyname](https://github.com/bruhismyname)

---

**Made with ❤️ by bruhismyname**

*Transform your ideas into profitable SaaS businesses!*
