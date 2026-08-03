# MailHog Fresh System Commands

Commands and configuration needed after pulling this project on a new system.

## 1. Clone And Enter Project

```bash
git clone <your-repository-url>
cd Placement-Portal-Application-MAD-II
```

## 2. Backend Setup

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### macOS/Linux

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Create `backend/.env`

Create `backend/.env` with this content:

```env
SECRET_KEY=placement-portal-dev-secret-2024
JWT_SECRET_KEY=jwt-placement-portal-dev-secret-2024

REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=false
MAIL_USERNAME=dev@placement-portal.local
MAIL_PASSWORD=mailhog
MAIL_SENDER=noreply@placement-portal.local

SMS_PROVIDER=console
GCHAT_WEBHOOK_URL=
```

## 4. Install And Run MailHog

### Windows

Download `MailHog.exe` from:

```text
https://github.com/mailhog/MailHog/releases
```

Run:

```powershell
.\MailHog.exe
```

### macOS

```bash
brew install mailhog
mailhog
```

### Linux

```bash
wget https://github.com/mailhog/MailHog/releases/download/v1.0.1/MailHog_linux_amd64
chmod +x MailHog_linux_amd64
./MailHog_linux_amd64
```

MailHog inbox:

```text
http://localhost:8025
```

MailHog SMTP:

```text
localhost:1025
```

## 5. Start Redis

### Windows

Install Memurai or Redis for Windows, then start the Redis service.

Verify:

```powershell
Test-NetConnection localhost -Port 6379
```

### macOS

```bash
brew install redis
brew services start redis
redis-cli ping
```

### Linux

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
redis-cli ping
```

Expected response:

```text
PONG
```

## 6. Start Backend API

From `backend` with virtual environment activated:

```bash
python app.py
```

Backend URL:

```text
http://localhost:5000
```

## 7. Start Celery Worker

Open a new terminal.

```bash
cd backend
```

Activate the virtual environment, then run:

```bash
python run_worker.py
```

## 8. Start Celery Beat

Open another terminal.

```bash
cd backend
```

Activate the virtual environment, then run:

```bash
python run_beat.py
```

Monthly report schedule:

```text
First day of every month at 06:00 UTC
```

## 9. Frontend Setup

From the project root:

```bash
npm install
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

## 10. Verify MailHog Email Logging

1. Open `http://localhost:8025`.
2. Log in as admin.
3. Generate a Monthly Activity Report from Admin Reports.
4. Confirm an email appears in MailHog.
5. Confirm the CSV report is attached.

Default admin, if unchanged:

```text
Email: admin@admin.com
Password: password
```
