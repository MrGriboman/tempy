from flask import Flask, jsonify, render_template, request
import mysql.connector
import pandas as pd
import plotly.express as px
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Database configuration
load_dotenv()
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

TABLE_DISPLAY_NAMES = {
    "TEMP_LOGS": "Все измерения",
    "HOURLY_TEMP": "Средняя по часам",
    "DAILY_TEMP": "Средняя по дням",
}

# Database connection helper
def query_db(query, args=(), one=False):
    conn = mysql.connector.connect(**DB_CONFIG)
    cur = conn.cursor(dictionary=True)
    cur.execute(query, args)
    results = cur.fetchall()
    conn.close()
    return (results[0] if results else None) if one else results

# List of available tables
TABLES = ["TEMP_LOGS", "HOURLY_TEMP", "DAILY_TEMP"]

# Route: Render the main page with plot
@app.route("/", methods=["GET", "POST"])
def home():
    selected_table = request.form.get("table", "TEMP_LOGS")  # Default to TEMP_LOGS
    start_date = request.form.get("start_date")  # Start date from form
    end_date = request.form.get("end_date")  # End date from form

    # Query data based on date range
    if start_date and end_date:
        query = f"SELECT * FROM {selected_table} WHERE timestamp BETWEEN %s AND %s"
        data = query_db(query, (start_date, end_date))
    else:
        data = query_db(f"SELECT * FROM {selected_table}")

    df = pd.DataFrame(data)

    if not df.empty:
        fig = px.line(df, x="TIMESTAMP", y="TEMPERATURE", title=f"{TABLE_DISPLAY_NAMES[selected_table]} (Температура/Время)")
        plot_html = fig.to_html(full_html=False)
    else:
        plot_html = "<p>Некорректно выбранные даты или нет данных за указанный период.</p>"

    return render_template("index.html", tables=TABLES, table_names=TABLE_DISPLAY_NAMES, selected_table=selected_table, start_date=start_date, end_date=end_date, plot_html=plot_html)

if __name__ == "__main__":
    app.run(debug=True)
