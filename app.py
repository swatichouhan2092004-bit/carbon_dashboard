# app.py (fixed, complete)
from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
import sqlite3, os, json, uuid, re
from datetime import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from process_questions import PROCESS_QUESTIONS

DB = "emissions.db"
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "super_secret_key_for_carbon_dashboard_project")

# --- Helpers ---
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def parse_float_safe(v):
    """Try to parse numeric user input to float, return None if not numeric."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if s == "":
        return None
    # remove commas and non-numeric trailing text
    s = s.replace(",", "")
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    if m:
        try:
            return float(m.group(0))
        except:
            return None
    return None

def dict_to_obj(d: dict):
    """Convert dict to simple object so templates can use dot notation."""
    class O: pass
    o = O()
    for k,v in d.items():
        setattr(o, k, v)
    return o

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    success = None
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == "POST":
        action = request.form.get("action")
        if action == "register":
            try:
                username = request.form["username"]
                password = request.form["password"]
                email = request.form["email"]
                nodal_person = request.form.get("nodal_person")
                designation = request.form.get("designation")
                company = request.form.get("company")
                phone = request.form.get("phone")

                hashed_password = generate_password_hash(password)
                user_uk = str(uuid.uuid4())

                conn = get_db(); cur = conn.cursor()
                cur.execute("""
                    INSERT INTO users (user_uk, username, password, nodal_person, designation, company, phone, email, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (user_uk, username, hashed_password, nodal_person, designation, company, phone, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                conn.commit(); conn.close()
                success = "Registration successful! Please log in."
            except sqlite3.IntegrityError:
                error = "Username or Email already exists."
            except Exception as e:
                error = f"Registration failed: {e}"

        elif action == "login":
            try:
                username = request.form["username"]
                password = request.form["password"]
                conn = get_db(); cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                user_row = cur.fetchone(); conn.close()
                if user_row and check_password_hash(user_row["password"], password):
                    # store as dict
                    session["user"] = dict(user_row)
                    return redirect(url_for('dashboard'))
                else:
                    error = "Invalid Username or Password."
            except Exception:
                error = "An error occurred during login."

    return render_template("index.html", error=error, success=success)

@app.route("/get_questions/<process_code>")
def get_questions(process_code):
    proc = PROCESS_QUESTIONS.get(process_code)
    if not proc:
        return jsonify({"questions": [], "operation": "single"})
    return jsonify({"questions": proc.get("fields", []), "operation": proc.get("operation", "single")})

@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

@app.route("/concepts")
def concepts():
    return render_template("concepts.html")

@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():
    # convert session user dict to object for templates
    user_dict = session["user"]
    user_obj = dict_to_obj(user_dict)

    conn = get_db(); cur = conn.cursor()
    # processes list
    cur.execute("SELECT * FROM emission_factors ORDER BY process_desc")
    processes = cur.fetchall()

    # user activity (last 10) for this user_uk
    user_uk = user_dict.get("user_uk")
    cur.execute("""
        SELECT id, process_code, process_desc, scope, unit, input_details, factor_used, emission, created_at
        FROM emissions
        WHERE user_uk = ?
        ORDER BY created_at DESC
        LIMIT 10
    """, (user_uk,))
    activity_data_rows = cur.fetchall()

    # format activity entries
    activities = []
    for r in activity_data_rows:
        d = dict(r)
        try:
            inputs = json.loads(d.get("input_details") or "{}")
            d['input_value_str'] = "; ".join([f"{k}: {v}" for k, v in inputs.items()])
        except:
            d['input_value_str'] = "N/A"
        activities.append(d)

    if request.method == "POST":
        proc = request.form.get("process")
        cur.execute("SELECT * FROM emission_factors WHERE process_code = ?", (proc,))
        p = cur.fetchone()
        if not p:
            conn.close()
            return render_template("calculator.html", processes=processes, user=user_obj, activities=activities, error="Invalid process selected.")

        # get factor, desc, unit
        process_desc = p["process_desc"]
        scope = p["scope"]
        unit = p["unit"]
        factor = float(p["factor"] or 0.0)

        # get process question definition
        proc_meta = PROCESS_QUESTIONS.get(proc, {})
        fields = proc_meta.get("fields", [])
        operation = proc_meta.get("operation", "single")

        # collect input details with friendly labels
        input_details = {}
        numeric_values = {}  # key -> float
        for f in fields:
            key = f.get("key")
            q = f.get("question")
            raw = request.form.get(key)
            input_details[q] = raw if raw is not None else ""
            num = parse_float_safe(raw)
            if num is not None:
                numeric_values[key] = num

        # Fallback: if no mapped fields (no questions), check existing 'quantity' form
        if not fields:
            raw_qty = request.form.get("quantity")
            num = parse_float_safe(raw_qty)
            if num is None:
                conn.close()
                return render_template("calculator.html", processes=processes, user=user_obj, activities=activities, error="Please enter a numeric quantity.")
            activity_value = num
        else:
            # compute activity_value based on operation
            activity_value = 0.0
            if operation == "multiply":
                prod = 1.0
                found = False
                for k,v in numeric_values.items():
                    prod *= v
                    found = True
                activity_value = prod if found else 0.0
            elif operation == "sum":
                s = sum(numeric_values.values()) if numeric_values else 0.0
                activity_value = s
            else:  # 'single' or default
                # choose the most relevant numeric field:
                # priority list of likely numeric keys
                priority = ["Fuel_Con", "Fuel_cons", "Total_Consumption", "Annual_cons", "Tot_Fuel_cons", "quantity", "Distance", "Distance_km", "Total_Consumption", "Total_Consumption_kWh", "Total_Consumption(kWh)"]
                picked = None
                for key in priority:
                    if key in numeric_values:
                        picked = numeric_values[key]; break
                if not picked and numeric_values:
                    # pick first numeric value
                    picked = next(iter(numeric_values.values()))
                activity_value = float(picked) if picked is not None else 0.0

                # special per-process adjustments:
                if proc == "TRANS_LMV_EM":
                    # if user entered Distance one-way, double it
                    if "Distance" in numeric_values:
                        activity_value = numeric_values.get("Distance", activity_value) * 2.0

        # Final emission calculation (activity_value x factor)
        emission = activity_value * factor

        # Save to DB under this user's user_uk
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute("""
            INSERT INTO emissions (user_uk, process_code, process_desc, scope, unit, input_details, factor_used, emission, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_uk, proc, process_desc, scope, unit, json.dumps(input_details, ensure_ascii=False), factor, emission, now))
        conn.commit()
        conn.close()
        return redirect(url_for('calculator'))

    conn.close()
    return render_template("calculator.html", processes=processes, user=user_obj, activities=activities)
    
@app.route("/dashboard")
@login_required
def dashboard():
    user_dict = session["user"]
    user_obj = dict_to_obj(user_dict)
    user_uk = user_dict.get("user_uk")
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT created_at, process_desc, scope, unit, input_details, emission
        FROM emissions
        WHERE user_uk = ?
        ORDER BY created_at DESC
    """, (user_uk,))
    rows = cur.fetchall()
    entries = []
    total_emission = 0.0
    scope_data = {}
    process_emissions = {}
    for r in rows:
        d = dict(r)
        try:
            d["input_details"] = json.loads(d.get("input_details") or "{}")
        except:
            d["input_details"] = {}
        entries.append(d)
        e = float(d.get("emission") or 0.0)
        total_emission += e
        scope = d.get("scope", "Unknown")
        scope_data[scope] = scope_data.get(scope, 0.0) + e
        process_emissions[d.get("process_desc","Unknown")] = process_emissions.get(d.get("process_desc","Unknown"), 0.0) + e
    conn.close()

    top = sorted(process_emissions.items(), key=lambda x:x[1], reverse=True)[:5]
    labels = [t[0] for t in top]; values = [round(t[1],2) for t in top]

    return render_template("dashboard.html", entries=entries, total_emission_kg=total_emission,
                           scope_data=scope_data, process_labels=labels, process_values=values, user=user_obj)

@app.route("/export_data")
@login_required
def export_data():
    user_uk = session["user"]["user_uk"]
    conn = get_db(); cur = conn.cursor()
    cur.execute("""
        SELECT created_at, process_desc, scope, unit, input_details, factor_used, emission
        FROM emissions
        WHERE user_uk = ?
        ORDER BY created_at DESC
    """, (user_uk,))
    rows = cur.fetchall(); conn.close()
    csv = "Date,Process Description,Scope,Unit,Activity Details,Emission Factor (kg CO2e/unit),Emission (kg CO2e)\n"
    for r in rows:
        r_dict = dict(r)
        try:
            inputs = json.loads(r_dict.get('input_details','{}'))
            input_str = "; ".join([f"{k}: {v}" for k,v in inputs.items()])
        except:
            input_str = ""
        csv += f"{r_dict['created_at']},\"{r_dict['process_desc']}\",{r_dict['scope']},{r_dict['unit']},\"{input_str.replace('\"','\"\"')}\",{r_dict['factor_used']},{r_dict['emission']}\n"
    return Response(csv, mimetype="text/csv", headers={"Content-disposition": "attachment; filename=carbon_emissions_report.csv"})

if __name__ == "__main__":
    app.run(debug=True)
