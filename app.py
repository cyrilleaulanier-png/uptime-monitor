import os
import threading
from flask import Flask, render_template
import psycopg2
from psycopg2.extras import RealDictCursor

# Importer la fonction de vérification depuis checker.py
from checker import run_monitoring_loop

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/uptime_db"
)


def get_db_connection():
  return psycopg2.connect(DATABASE_URL)


@app.route("/")
def dashboard():
  try:
    query_latest = """
            SELECT DISTINCT ON (site) site, statut, latence_ms, verifie_le
            FROM checks
            ORDER BY site, verifie_le DESC;
        """
    query_stats = """
            SELECT 
                site,
                COUNT(*) as total_checks,
                ROUND((COUNT(*) FILTER (WHERE statut = 'en ligne') * 100.0 / COUNT(*)), 1) as uptime_percent,
                ROUND(AVG(latence_ms)::numeric, 1) as avg_latency_ms
            FROM checks
            GROUP BY site;
        """
    query_recent = """
            SELECT site, statut, latence_ms, verifie_le
            FROM checks
            ORDER BY verifie_le DESC
            LIMIT 10;
        """

    with get_db_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query_latest)
        latest_checks = cur.fetchall()

        cur.execute(query_stats)
        stats = {row["site"]: row for row in cur.fetchall()}

        cur.execute(query_recent)
        recent_history = cur.fetchall()

    status_cards = []
    for item in latest_checks:
      site_stats = stats.get(
          item["site"], {"uptime_percent": 0.0, "avg_latency_ms": 0.0}
      )
      status_cards.append({
          "site": item["site"],
          "statut": item["statut"],
          "latence_ms": item["latence_ms"],
          "verifie_le": item["verifie_le"],
          "uptime_percent": site_stats["uptime_percent"],
          "avg_latency_ms": site_stats["avg_latency_ms"],
      })

    return render_template(
        "index.html", cards=status_cards, history=recent_history
    )

  except Exception as e:
    return f"""
        <div style="font-family: sans-serif; padding: 40px; text-align: center;">
            <h2>🚀 Le Dashboard Ops est en cours de démarrage...</h2>
            <p>Détail : {e}</p>
        </div>
        """, 200


# Lancer le worker checker en tâche de fond au démarrage
def start_background_checker():
  thread = threading.Thread(target=run_monitoring_loop, daemon=True)
  thread.start()


start_background_checker()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)