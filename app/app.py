import os
import psycopg2
from flask import Flask, render_template

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=os.environ.get("DB_PORT", "5432"),
        database=os.environ["DB_NAME"],
        user=os.environ["DB_USERNAME"],
        password=os.environ["DB_PASSWORD"]
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {
        "application": "Employeehub",
        "status": "healthy"
    }


@app.route("/db-test")
def db_test():
    try:
        connection = get_db_connection()

        cursor = connection.cursor()
        cursor.execute("SELECT version();")

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return {
            "database": "connected",
            "version": result[0]
        }

    except Exception as e:
        return {
            "database": "connection failed",
            "error": str(e)
        }, 500