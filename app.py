from flask import Flask, request
import sqlite3

app = Flask(__name__)

conn = sqlite3.connect("aquaalert.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS reports(
id INTEGER PRIMARY KEY AUTOINCREMENT,
village TEXT,
cases INTEGER,
water TEXT,
risk TEXT
)
""")

conn.commit()

@app.route('/')
def home():
    return '''
    <h1>AquaAlert</h1>

    <form action="/check" method="post">
        Village Name:
        <input type="text" name="village"><br><br>

        Disease Cases:
        <input type="number" name="cases"><br><br>

        Water Quality:
        <select name="water">
            <option value="Good">Good</option>
            <option value="Bad">Bad</option>
        </select><br><br>

        <input type="submit" value="Check Risk">
    </form>
    '''

@app.route('/check', methods=['POST'])
def check():
    village = request.form['village']
    cases = int(request.form['cases'])
    water = request.form['water']

    if cases > 10 or water == "Bad":
        risk = "High"
    else:
        risk = "Low"

    cursor.execute(
        "INSERT INTO reports(village,cases,water,risk) VALUES(?,?,?,?)",
        (village, cases, water, risk)
    )

    conn.commit()

    return f"<h2>{risk} RISK in {village}</h2>"
@app.route('/report')
def report():
    cursor.execute("SELECT village, cases, water, risk FROM reports")
    rows = cursor.fetchall()

    html = """
    <h1>AquaAlert Reports</h1>

    <table border="1">
        <tr>
            <th>Village</th>
            <th>Cases</th>
            <th>Water Quality</th>
            <th>Risk</th>
        </tr>
    """

    for row in rows:
        html += f"""
        <tr>
            <td>{row[0]}</td>
            <td>{row[1]}</td>
            <td>{row[2]}</td>
            <td>{row[3]}</td>
        </tr>
        """

    html += "</table>"

    return html
@app.route('/dashboard')
def dashboard():

    cursor.execute("SELECT COUNT(*) FROM reports")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE risk='High'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE risk='Low'")
    low = cursor.fetchone()[0]

    return f"""
    <h1>AquaAlert Dashboard</h1>

    <h3>Total Villages: {total}</h3>
    <h3>High Risk Villages: {high}</h3>
    <h3>Low Risk Villages: {low}</h3>
    """

app.run(host="0.0.0.0", port=5000)