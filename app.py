import os
import threading
from flask import Flask, redirect, render_template, request, url_for
import psycopg2
from psycopg2.extras import RealDictCursor

from checker import run_monitoring_loop

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/uptime_db"
)
if DATABASE_URL.startswith("postgres://"):
  DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


def get_db_connection():
  return psycopg2.connect(DATABASE_URL)


# Initialisation de la table des sites à surveiller
def init_db():
  with get_db_connection() as conn:
    with conn.cursor() as cur:
      cur.execute("""
                CREATE TABLE IF NOT EXISTS targets (
                    id SERIAL PRIMARY KEY,
                    url VARCHAR(255) UNIQUE NOT NULL
                );
            """)
      # Insérer quelques sites par défaut si la table est vide
      cur.execute("SELECT COUNT(*) FROM targets;")
      if cur.fetchone()[0] == 0:
        cur.execute("""
                    INSERT INTO targets (url) VALUES 
                    ('https://www.google.com'),
                    ('https://www.github.com')
                    ON CONFLICT DO NOTHING;
                """)
    conn.commit()


@app.route("/")
def dashboard():
  try:
    query_latest = """
            SELECT DISTINCT ON (c.site) c.site, c.statut, c.latence_ms, c.verifie_le
            FROM checks c
            INNER JOIN targets t ON c.site = t.url
            ORDER BY c.site, c.verifie_le DESC;
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
    query_targets = "SELECT url FROM targets ORDER BY url;"

    with get_db_connection() as conn:
      with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(query_targets)
        targets = [row["url"] for row in cur.fetchall()]

        cur.execute(query_latest)
        latest_checks = cur.fetchall()

        cur.execute(query_stats)
        stats = {row["site"]: row for row in cur.fetchall()}

        cur.execute(query_recent)
        recent_history = cur.fetchall()

    status_cards = []
    # On boucle sur les sites cibles actifs
    for site in targets:
      item = next((c for c in latest_checks if c["site"] == site), None)
      site_stats = stats.get(
          site, {"uptime_percent": 0.0, "avg_latency_ms": 0.0}
      )

      status_cards.append({
          "site": site,
          "statut": item["statut"] if item else "En attente...",
          "latence_ms": item["latence_ms"] if item else 0,
          "verifie_le": item["verifie_le"] if item else "Jamais",
          "uptime_percent": site_stats["uptime_percent"],
          "avg_latency_ms": site_stats["avg_latency_ms"],
      })

    return render_template(
        "index.html", cards=status_cards, history=recent_history
    )

  except Exception as e:
    return f"<h2>Erreur : {e}</h2>", 200


# Action : Ajouter un site
@app.route("/add_site", methods=["POST"])
def add_site():
  new_url = request.form.get("url")
  if new_url:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
            "INSERT INTO targets (url) VALUES (%s) ON CONFLICT DO NOTHING;",
            (new_url,),
        )
      conn.commit()
  return redirect(url_for("dashboard"))


# Action : Supprimer un site (et son historique)
@app.route("/delete_site", methods=["POST"])
def delete_site():
  site_to_delete = request.form.get("url")
  if site_to_delete:
    with get_db_connection() as conn:
      with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM targets WHERE url = %s;", (site_to_delete,)
        )
        cur.execute(
            "DELETE FROM checks WHERE site = %s;", (site_to_delete,)
        )
      conn.commit()
  return redirect(url_for("dashboard"))


init_db()

# Lancement du worker d'arrière-plan
thread = threading.Thread(target=run_monitoring_loop, daemon=True)
thread.start()

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)