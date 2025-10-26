import os
import datetime
import logging
from threading import Thread
from flask import Flask, jsonify, request

app = Flask(__name__)

# start time
start_time = datetime.datetime.utcnow()

# logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

@app.route("/")
def home():
    # sprawdź X-Forwarded-For (jeśli proxy) lub remote_addr
    forwarded = request.headers.get("X-Forwarded-For", "")
    ip = forwarded.split(",")[0].strip() if forwarded else request.remote_addr
    logger.info(f"Received ping from {ip}")
    return "✅ Bot działa i żyje!"

@app.route("/status")
def status():
    uptime = datetime.datetime.utcnow() - start_time
    return jsonify({
        "status": "running",
        "uptime": str(uptime),
        "started": start_time.replace(microsecond=0).isoformat() + "Z"
    })

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    # debug=False w produkcji
    app.run(host="0.0.0.0", port=port, debug=False)

def keep_alive():
    thread = Thread(target=run_flask)
    thread.daemon = True
    thread.start()
    logger.info("🌐 Keep-alive webserver started.")

# Jeżeli chcesz uruchomić serwer flask z wątkiem keep-alive (np. lokalnie), użyj:
if __name__ == "__main__":
    # do debugu lokalnego możesz odpalić keep_alive() i potem resztę (np. bota)
    keep_alive()
    # tutaj możesz ewentualnie uruchomić pętlę main bota synchronously,
    # lub po prostu blokować program (np. input()) jeśli bot działa w innym wątku.
    import time
    while True:
        time.sleep(3600)
