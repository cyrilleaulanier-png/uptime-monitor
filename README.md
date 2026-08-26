# 📊 Uptime Monitor & Ops Dashboard

Un outil de supervision d'uptime léger, conteneurisé et déployé sur le Cloud pour vérifier la disponibilité et la latence de services web en temps réel.

🌐 **Démo en ligne :** (https://uptime-monitor-3.onrender.com)

---

## 🚀 Fonctionnalités
- 🟢 **Monitoring continu :** Vérification automatique de l'état HTTP et de la latence (ms) des sites cibles.
- ➕ **Gestion dynamique :** Ajout et suppression d'URL à surveiller en direct depuis le Dashboard.
- 📈 **Statistiques en direct :** Calcul automatique du taux de disponibilité (% Uptime) et de la latence moyenne.
- 🐳 **Prêt pour la production :** Déploiement entièrement conteneurisé avec Docker Compose.
- 🔄 **Pipeline CI/CD :** Validation automatique du code via GitHub Actions et déploiement continu sur Render.

---

## 🛠️ Stack Technique
* **Backend :** Python 3.11, Flask, Requests, Threading
* **Base de données :** PostgreSQL (`psycopg2`)
* **Conteneurisation :** Docker, Docker Compose
* **Automation & Cloud :** GitHub Actions (CI), Render (CD / PaaS)

---

## 💻 Installation & Lancement en local

### Prérequis
- [Docker Desktop](https://www.docker.com/) installé et lancé.

### Étape 1 : Cloner le dépôt
```bash
git clone [https://github.com/cyrilleaulanier-png/uptime-monitor.git](https://github.com/cyrilleaulanier-png/uptime-monitor.git)
cd uptime-monitor
