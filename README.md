# 3D Server

FastAPI backend server for 3D application.

## One-Click Deploy to Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/fastapi?referralCode=alphasec)

## Environment Variables

Make sure to set these environment variables in Railway:

- `DB_HOST` - MySQL host
- `DB_USER` - MySQL user
- `DB_PASSWORD` - MySQL password
- `DB_NAME` - MySQL database name
- `SECRET_KEY` - Secret key for JWT tokens

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with required environment variables

3. Run the server:
```bash
uvicorn app.main:app --reload
```
 
