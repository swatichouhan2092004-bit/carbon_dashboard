import sqlite3
import pandas as pd

# Connect to SQLite database
conn = sqlite3.connect("emissions.db")
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS emission_factors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    process TEXT,
    fuel_type TEXT,
    activity_data REAL,
    emission_factor REAL,
    co2_emission REAL,
    ch4_emission REAL,
    n2o_emission REAL,
    total_emission REAL
)
""")
conn.commit()

# Read Excel file
excel_file = "Master Calculation.xlsx"
df = pd.read_excel(excel_file)

# Clear previous data
cur.execute("DELETE FROM emission_factors")

# Insert rows
for _, row in df.iterrows():
    cur.execute("""
        INSERT INTO emission_factors (
            process, fuel_type, activity_data, emission_factor,
            co2_emission, ch4_emission, n2o_emission, total_emission
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        row.get("Process"),
        row.get("Fuel Type"),
        row.get("Activity Data"),
        row.get("Emission Factor"),
        row.get("CO2 Emission"),
        row.get("CH4 Emission"),
        row.get("N2O Emission"),
        row.get("Total Emission")
    ))

conn.commit()
conn.close()
print("✅ Excel data imported successfully into emissions.db!")
