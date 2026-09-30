from flask import Flask, request, render_template_string, redirect, url_for
from datetime import datetime
from urllib.parse import quote

app = Flask(__name__)

reports = []
next_id = 1


HTML = """
<!DOCTYPE html>
<html>

<head>

    <title>Smart Traffic Reporting</title>

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <style>

        body {
            font-family: Arial;
            background: #f2f2f2;
            padding: 15px;
            margin: 0;
        }

        .box {
            max-width: 750px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
        }

        h1 {
            text-align: center;
        }

        input, select, textarea, button {
            width: 100%;
            padding: 11px;
            margin: 8px 0;
            box-sizing: border-box;
        }

        button {
            background: black;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        .report {
            border: 1px solid #ddd;
            padding: 15px;
            margin-top: 15px;
            border-radius: 8px;
        }

        .high {
            border-left: 6px solid red;
        }

        .medium {
            border-left: 6px solid orange;
        }

        .low {
            border-left: 6px solid green;
        }

        .stats {
            background: #eeeeee;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }

        .danger {
            color: red;
            font-weight: bold;
        }

        .success {
            color: green;
            font-weight: bold;
        }

        a {
            text-decoration: none;
        }

    </style>

</head>


<body>

<div class="box">

<h1>🚦 Smart Traffic Reporting</h1>


<!-- REPORT FORM -->

<h2>📝 Report Traffic Problem</h2>

<form method="POST" action="/report">

    <input
        name="location"
        placeholder="Enter location"
        required
    >

    <select name="traffic">

        <option>Low</option>
        <option>Medium</option>
        <option>High</option>
        <option>Very High</option>

    </select>


    <select name="problem">

        <option>Traffic Jam</option>
        <option>Accident</option>
        <option>Road Damage</option>
        <option>Signal Problem</option>

    </select>


    <textarea
        name="description"
        placeholder="Describe the problem"
    ></textarea>


    <button type="submit">
        🚨 Submit Report
    </button>

</form>


<!-- SEARCH -->

<h2>🔎 Search Reports</h2>

<form method="GET" action="/">

    <input
        name="search"
        placeholder="Search location or problem"
        value="{{ search }}"
    >

    <button type="submit">
        Search
    </button>

</form>


<!-- STATISTICS -->

<div class="stats">

<h2>📊 Traffic Dashboard</h2>

<p>
Total Reports:
<b>{{ total }}</b>
</p>

<p>
🚗 Traffic Jams:
<b>{{ traffic_jams }}</b>
</p>

<p>
🚑 Accidents:
<b>{{ accidents }}</b>
</p>

<p>
🔴 High Traffic Reports:
<b>{{ high_traffic }}</b>
</p>

<p>
✅ Resolved Reports:
<b>{{ resolved }}</b>
</p>

</div>


<!-- REPORTS -->

<h2>📋 Traffic Reports</h2>


{% if filtered_reports %}

{% for r in filtered_reports %}

<div class="report
{% if r.traffic == 'Very High' or r.problem == 'Accident' %}
high
{% elif r.traffic == 'High' %}
medium
{% else %}
low
{% endif %}
">

<p>
<b>Report ID:</b> #{{ r.id }}
</p>

<p>
<b>📍 Location:</b>
{{ r.location }}
</p>


<p>
<b>🚦 Traffic:</b>
{{ r.traffic }}
</p>


<p>
<b>⚠️ Problem:</b>
{{ r.problem }}
</p>


<p>
<b>📝 Description:</b>
{{ r.description }}
</p>


<p>
<b>🕒 Reported:</b>
{{ r.time }}
</p>


{% if r.status == "Resolved" %}

<p class="success">
✅ Status: Resolved
</p>

{% else %}

<p class="danger">
🔴 Status: Pending
</p>

{% endif %}


<p>

<a
href="https://www.google.com/maps/search/?api=1&query={{ r.map_location }}"
target="_blank"
>

<button type="button">
🗺️ Open in Google Maps
</button>

</a>

</p>


{% if r.status != "Resolved" %}

<form
method="POST"
action="/resolve/{{ r.id }}"
>

<button type="submit">
✅ Mark as Resolved
</button>

</form>

{% endif %}


</div>

{% endfor %}

{% else %}

<p>
No reports found.
</p>

{% endif %}


</div>

</body>

</html>
"""


# ---------------------------------
# HOME PAGE
# ---------------------------------

@app.route("/")
def home():

    search = request.args.get("search", "").lower()

    if search:

        filtered_reports = [

            r for r in reports

            if search in r["location"].lower()
            or search in r["problem"].lower()
            or search in r["traffic"].lower()

        ]

    else:

        filtered_reports = reports


    total = len(reports)

    traffic_jams = sum(
        1 for r in reports
        if r["problem"] == "Traffic Jam"
    )

    accidents = sum(
        1 for r in reports
        if r["problem"] == "Accident"
    )

    high_traffic = sum(
        1 for r in reports
        if r["traffic"] in ["High", "Very High"]
    )

    resolved = sum(
        1 for r in reports
        if r["status"] == "Resolved"
    )


    return render_template_string(

        HTML,

        filtered_reports=filtered_reports,

        search=search,

        total=total,

        traffic_jams=traffic_jams,

        accidents=accidents,

        high_traffic=high_traffic,

        resolved=resolved

    )


# ---------------------------------
# SUBMIT REPORT
# ---------------------------------

@app.route("/report", methods=["POST"])
def report():

    global next_id


    location = request.form["location"]

    traffic = request.form["traffic"]

    problem = request.form["problem"]

    description = request.form["description"]


    # Create Google Maps search location

    map_location = quote(location)


    new_report = {

        "id": next_id,

        "location": location,

        "traffic": traffic,

        "problem": problem,

        "description": description,

        "time": datetime.now().strftime(
            "%d-%m-%Y %I:%M %p"
        ),

        "status": "Pending",

        "map_location": map_location

    }


    reports.append(new_report)

    next_id += 1


    return redirect(url_for("home"))


# ---------------------------------
# MARK REPORT AS RESOLVED
# ---------------------------------

@app.route("/resolve/<int:report_id>", methods=["POST"])
def resolve(report_id):

    for r in reports:

        if r["id"] == report_id:

            r["status"] = "Resolved"

            break


    return redirect(url_for("home"))


# ---------------------------------
# RUN APP
# ---------------------------------

app.run(debug=True)