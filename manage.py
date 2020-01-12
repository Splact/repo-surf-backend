from src import app


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"], access_log=False, workers=app.config["WORKERS"])
