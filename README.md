# 📊 Uptime Monitor & Ops Dashboard

A lightweight, containerized uptime monitoring tool deployed to the Cloud to track the availability and latency of web services in real time.

🌐 **Live Demo:** (https://uptime-monitor-3.onrender.com)

---

## 🚀 Features
- 🟢 **Continuous Monitoring:** Automatic checks for HTTP status and latency (ms) of targeted websites.
- ➕ **Dynamic Management:** Add and delete URLs to monitor directly from the Dashboard interface.
- 📈 **Live Analytics:** Automated calculation of availability rate (% Uptime) and average response time.
- 🐳 **Production-Ready:** Fully containerized setup using Docker Compose.
- 🔄 **CI/CD Pipeline:** Automated syntax checks via GitHub Actions and continuous deployment on Render.

---

## 🛠️ Tech Stack
* **Backend:** Python 3.11, Flask, Requests, Threading
* **Database:** PostgreSQL (`psycopg2`)
* **Containerization:** Docker, Docker Compose
* **Automation & Cloud:** GitHub Actions (CI), Render (CD / PaaS)

---

## 💻 Local Installation & Setup

### Prerequisites
- [Docker Desktop](https://www.docker.com/) installed and running.

### Step 1: Clone the repository
```bash
git clone [https://github.com/cyrilleaulanier-png/uptime-monitor.git](https://github.com/cyrilleaulanier-png/uptime-monitor.git)
cd uptime-monitor

### Step 2: Run with Docker Compose
```bash
docker compose up -d --build
