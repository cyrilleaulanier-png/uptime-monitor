import os
import time
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import requests

# Intervalle en secondes entre deux vérifications
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 30))

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/uptime_db"
)

SITES = [
    "https://www.google.com",
    "https://www.github.com",
    "https://apple.com",
    "https://cyrilleaulanier.com",
    "https://www.google.com/reader/about",
]


def get_db_connection():
  return psycopg2.connect(DATABASE_URL)


def init_db():
  with get_db_connection() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                CREATE TABLE IF NOT EXISTS checks (
                    id SERIAL PRIMARY KEY,
                    site VARCHAR(255) NOT NULL,
                    statut VARCHAR(50) NOT NULL,
                    latence_ms FLOAT NOT NULL,
                    verifie_le TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
      conn.commit()


def check_site(url):
  start_time = time.time()
  try:
    response = requests.get(url, timeout=5)
    latency_ms = round((time.time() - start_time) * 1000, 2)
    statut = (
        "en ligne"
        if response.status_code == 200
        else f"problème ({response.status_code})"
    )
    return statut, latency_ms
  except requests.exceptions.RequestException:
    latency_ms = round((time.time() - start_time) * 1000, 2)
    return "injoignable", latency_ms


def check_all_sites():
  resultats = []
  for site in SITES:
    statut, latence = check_site(site)
    resultats.append({
        "site": site,
        "statut": statut,
        "latence_ms": latence,
        "verifie_le": datetime.now(),
    })
  return resultats


def save_results_to_db(resultats):
  with get_db_connection() as conn:
    with conn.cursor() as cur:
      for r in resultats:
        cur.execute(
            """
                    INSERT INTO checks (site, statut, latence_ms, verifie_le)
                    VALUES (%s, %s, %s, %s)
                """,
            (r["site"], r["statut"], r["latence_ms"], r["verifie_le"]),
        )
      conn.commit()


def run_monitoring_loop():
  """Boucle infinie qui s'exécute automatiquement toutes les X secondes."""
  init_db()
  print(
      f"🚀 Worker Ops démarré ! Vérification toutes les {CHECK_INTERVAL}"
      " secondes."
  )
  print("Appuie sur Ctrl+C pour arrêter le script.\n")

  try:
    while True:
      print(f"[{datetime.now().strftime('%H:%M:%S')}] Lancement du check...")
      resultats = check_all_sites()
      save_results_to_db(resultats)
      print(" -> Sauvegardé en BDD.")
      time.sleep(CHECK_INTERVAL)
  except KeyboardInterrupt:
    print("\n🛑 Arrêt du monitoring.")


if __name__ == "__main__":
  run_monitoring_loop()