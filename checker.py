import os
import time
import psycopg2
import requests

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/uptime_db"
)
if DATABASE_URL.startswith("postgres://"):
  DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_db_connection():
  return psycopg2.connect(DATABASE_URL)


def get_active_sites():
  try:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute("SELECT url FROM targets;")
        return [row[0] for row in cur.fetchall()]
  except Exception:
    return []


def check_site(url):
  try:
    response = requests.get(url, timeout=5)
    statut = (
        "en ligne"
        if response.status_code == 200
        else f"erreur ({response.status_code})"
    )
    latence_ms = int(response.elapsed.total_seconds() * 1000)
  except requests.RequestException:
    statut = "hors ligne"
    latence_ms = 0
  return statut, latence_ms


def save_check(site, statut, latence_ms):
  query = "INSERT INTO checks (site, statut, latence_ms) VALUES (%s, %s, %s);"
  with get_db_connection() as conn:
    with conn.cursor() as cur:
      cur.execute(query, (site, statut, latence_ms))
    conn.commit()


def run_monitoring_loop():
  check_interval = int(os.getenv("CHECK_INTERVAL", 30))
  while True:
    sites = get_active_sites()
    for site in sites:
      statut, latence_ms = check_site(site)
      save_check(site, statut, latence_ms)
    time.sleep(check_interval)


if __name__ == "__main__":
  run_monitoring_loop()