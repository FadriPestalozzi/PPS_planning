from flask import Flask, render_template, jsonify
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/time_data")
def time_data():
    now = datetime.datetime.now()
    values = [
        now.year,
        now.month,
        now.day,
        now.isocalendar()[1],  # week
        now.hour,
        now.minute,
        now.second
    ]
    return jsonify({"values": values})

if __name__ == "__main__":
    app.run(debug=True)