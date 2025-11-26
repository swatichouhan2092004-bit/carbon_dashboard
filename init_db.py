# init_db.py
"""
Final robust initializer (fixed datetime serialization):
- reads Master Calculation.xlsx
- loads emission factors from 'Emission_factor' sheet (parses numeric EF)
- falls back to IPCC_FACTORS_BY_CODE when EF missing
- uses FORMULAS dict for derived totals per-sheet
- safely serializes datetime and timestamp values in JSON
"""

import sqlite3, os, re, json
import pandas as pd
import numpy as np
from datetime import datetime, date

DB = "emissions.db"
EXCEL = "Master Calculation.xlsx"

# === FALLBACK FACTORS ===
IPCC_FACTORS_BY_CODE = {
    "DG_CONS_EM": 2.68, "LPG_CONS_EM": 2.94, "COMP_EM": 0.03, "BLAST_EM": 1.20,
    "OVER_B_EM": 0.05, "HEMV_FUEL_EM": 2.68, "LMV_EM_D": 2.68, "LMV_EM_G": 2.31,
    "PUMP_DEW_EM": 2.68, "PORT_DG_EM": 2.68, "AC_EM": 1430.0, "OXY_ACE_EM": 25.0,
    "DIESEL_DRILL_EM": 2.68, "LUBE_USE_EM": 3.10, "MIN_QC_TRANS_EM": 2.68,
    "ELECT_EM": 0.82, "CORE_QC_TRANS_EM": 2.68, "DRILL_BIL_PROD_EM": 15.0,
    "LUBE_PROD_EM": 4.5, "PVC_BOX_PROD_EM": 1.5, "HEMV_TYRE_PROD_EM": 150.0,
    "LMV_TYRE_PROD_EM": 12.0, "BATT_PROD_EM": 12.0, "BLAST_PROD_EM": 1.2,
    "OXY_ACE_PROD_EM": 0.5, "ELECT_ARC_PROD_EM": 25.0, "HDPE5_PROD_EM": 2.5,
    "HDPE4.5_PROD_EM": 2.2, "LPG_PROD_EM": 1.0, "FE_CHROM_PROD_EM": 3.0,
    "STEEL_PROD_EM": 2.0, "WTP_ELECT_EM": 0.82, "QC_CHEM_PROD_EM": 5.0,
    "CHEM_ETP_PROD_EM": 5.0, "DISP_TYRE_EM": 150.0, "DISP_LUBE_EM": 3.1,
    "TRANS_2WHS_EM": 0.06, "TRANS_4WHS_EM": 0.19, "TRANS_BUS_EM": 0.03,
    "TRANS_PLANE_EM": 0.25, "TRANS_LMV_EM": 0.19, "TRANS_6WHS_EM": 2.68,
    "TRANS_12_14WHS_EM": 2.68, "GEN_ITEM_PROD_EM": 5.0, "CORE_TRANS_BB_EM": 2.68
}

# === FORMULAS ===
FORMULAS = {
    "LPG_CONS_EM": "row.get('LPG_no',0) * row.get('Weight_LPG',0)",
    "DG_CONS_EM": "row.get('Fuel_cons',0)",
    "COMP_EM": "row.get('Compost_gen',0)",
    "HEMV_FUEL_EM": "row.get('Fuel_Con',0) or row.get('Fuel_Cons',0)",
    "OVER_B_EM": "row.get('T',0) or row.get('t',0) or row.get('m3',0)"
}

# === HELPERS ===
def parse_number(v):
    """Extract numeric value safely."""
    if pd.isna(v): return 0.0
    if isinstance(v, (int, float, np.integer, np.floating)): return float(v)
    s = str(v).replace(",", "").strip()
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    return float(m.group(0)) if m else 0.0

def safe_eval_formula(formula, row):
    """Safely evaluate formulas."""
    try:
        return float(eval(formula, {"__builtins__": {}}, {"row": row}))
    except Exception:
        return 0.0

def safe_json_dumps(data):
    """Convert datetime, Timestamp, and NumPy types before dumping JSON."""
    def convert(obj):
        if isinstance(obj, (datetime, date, pd.Timestamp)):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, (np.ndarray, list)):
            return [convert(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: convert(v) for k, v in obj.items()}
        else:
            return obj
    return json.dumps(convert(data), ensure_ascii=False)

# === DATABASE CREATION ===
def recreate_db():
    if os.path.exists(DB):
        os.remove(DB)
        print("🗑 Deleted old DB")
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.executescript("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uk TEXT UNIQUE, username TEXT UNIQUE, password TEXT,
        nodal_person TEXT, designation TEXT, company TEXT, phone TEXT, email TEXT UNIQUE, created_at TEXT
    );
    CREATE TABLE emission_factors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        process_code TEXT UNIQUE, process_desc TEXT, scope TEXT, unit TEXT, factor REAL DEFAULT 0,
        calc_type TEXT DEFAULT 'single', last_updated TEXT
    );
    CREATE TABLE emissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_uk TEXT, process_code TEXT, process_desc TEXT, scope TEXT, unit TEXT,
        input_details TEXT, factor_used REAL, emission REAL, created_at TEXT
    );
    """)
    conn.commit()
    print("✅ DB created.")
    return conn

# === LOAD FACTOR SHEET ===
def load_factors_sheet():
    xls = pd.ExcelFile(EXCEL, engine='openpyxl')
    if "Emission_factor" not in xls.sheet_names:
        raise RuntimeError("Emission_factor sheet not found.")
    df = xls.parse("Emission_factor")
    df.columns = [str(c).strip() for c in df.columns]
    proc_col = next((c for c in df.columns if 'process' in c.lower()), None)
    ef_col = next((c for c in df.columns if 'ef' in c.lower() or 'factor' in c.lower()), None)
    unit_col = next((c for c in df.columns if 'unit' in c.lower()), None)
    desc_col = next((c for c in df.columns if 'desc' in c.lower()), None)
    scope_col = next((c for c in df.columns if 'scope' in c.lower()), None)
    mapping = {}
    for _, r in df.iterrows():
        code = str(r.get(proc_col)).strip().upper() if r.get(proc_col) else None
        if not code: continue
        factor = parse_number(r.get(ef_col))
        mapping[code] = {
            "factor": factor,
            "unit": str(r.get(unit_col) or "").strip(),
            "desc": str(r.get(desc_col) or "").strip(),
            "scope": str(r.get(scope_col) or "").strip(),
        }
    return mapping

def insert_factors_to_db(conn, mapping):
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0; from_sheet=0; fallback=0
    all_codes = set(mapping.keys()) | set(IPCC_FACTORS_BY_CODE.keys())
    for code in sorted(all_codes):
        entry = mapping.get(code, {})
        factor = entry.get("factor") or IPCC_FACTORS_BY_CODE.get(code, 0.0)
        if not factor: continue
        unit = entry.get("unit") or ""
        desc = entry.get("desc") or f"Emission from {code}"
        scope = entry.get("scope") or ("Scope_1" if "TRANS" not in code and not code.endswith("PROD_EM") else "Scope_3")
        cur.execute("""
            INSERT INTO emission_factors (process_code, process_desc, scope, unit, factor, calc_type, last_updated)
            VALUES (?, ?, ?, ?, ?, 'single', ?)
            ON CONFLICT(process_code) DO UPDATE SET
                process_desc=excluded.process_desc, scope=excluded.scope, unit=excluded.unit, factor=excluded.factor, last_updated=excluded.last_updated
        """, (code, desc, scope, unit, factor, now))
        inserted += 1
    conn.commit()
    print(f"✅ emission_factors inserted/updated: {inserted}")

# === COMPUTE EMISSIONS ===
def compute_and_insert_emissions(conn, factors_map):
    xls = pd.ExcelFile(EXCEL, engine='openpyxl')
    cur = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inserted = 0; skipped_rows = []

    for sheet in xls.sheet_names:
        if sheet in ["Emission_factor", "Description", "Processess"]:
            continue
        try:
            df = xls.parse(sheet)
        except Exception as e:
            print(f"⚠️ Could not parse sheet {sheet}: {e}")
            continue
        if df.empty:
            continue

        df.columns = [str(c).strip() for c in df.columns]
        proc_col = next((c for c in df.columns if 'process' in c.lower()), None)
        total_col = next((c for c in df.columns if 'total' in c.lower()), None)
        formula = FORMULAS.get(sheet)

        for idx, r in df.iterrows():
            row = {c: parse_number(r.get(c)) for c in df.columns}
            row.update({c.lower(): parse_number(r.get(c)) for c in df.columns})
            code = str(r.get(proc_col)).strip().upper() if proc_col and r.get(proc_col) else sheet
            factor = factors_map.get(code, {}).get("factor", IPCC_FACTORS_BY_CODE.get(code, 0.0))

            if factor == 0:
                skipped_rows.append({"sheet": sheet, "row": idx, "reason": "no_factor"}); continue

            total_activity = 0.0
            if formula:
                total_activity = safe_eval_formula(formula, row)
            elif total_col:
                total_activity = parse_number(r.get(total_col))

            emission = total_activity * factor
            input_details = {c: (r.get(c).strftime("%Y-%m-%d %H:%M:%S") if isinstance(r.get(c), (datetime, pd.Timestamp)) else r.get(c)) for c in df.columns}

            cur.execute("""
                INSERT INTO emissions (user_uk, process_code, process_desc, scope, unit, input_details, factor_used, emission, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "COMPANY001", code, f"Emission from {code}",
                factors_map.get(code, {}).get("scope", "Scope_1"),
                factors_map.get(code, {}).get("unit", "varies"),
                safe_json_dumps(input_details),
                factor, emission, now
            ))
            inserted += 1

    conn.commit()
    print(f"✅ Inserted emissions rows: {inserted}, Skipped: {len(skipped_rows)}")

# === MAIN ===
if __name__ == "__main__":
    try:
        print("Starting DB initialization...")
        conn = recreate_db()
        factors_map = load_factors_sheet()
        print(f"Loaded {len(factors_map)} factor entries.")
        insert_factors_to_db(conn, factors_map)
        compute_and_insert_emissions(conn, factors_map)
        conn.close()
        print("🎯 Initialization complete.")
    except Exception as e:
        print("❌ Initialization failed:", e)
