# process_questions.py
# Mapping: process_code -> {"fields": [ {key, question, unit}... ], "operation": "multiply|sum|single"}
PROCESS_QUESTIONS = {
    "LPG_CONS_EM": {
        "fields": [
            {"key": "LPG_no", "question": "How many LPG cylinders were used?", "unit": "Nos"},
            {"key": "Weight_LPG", "question": "What is the weight of one LPG cylinder (kg)?", "unit": "kg"}
        ],
        "operation": "multiply"
    },
    "DG_CONS_EM": {
        "fields": [{"key": "Fuel_cons", "question": "Total DG fuel consumed (litres)?", "unit": "litres"}],
        "operation": "single"
    },
    "COMP_EM": {
        "fields": [{"key": "Compost_gen", "question": "Total compost generated (kg)?", "unit": "kg"}],
        "operation": "single"
    },
    "HEMV_FUEL_EM": {
        "fields": [
            {"key": "Type", "question": "Type of HEMV (text)", "unit": "-"},
            {"key": "Model", "question": "Model of HEMV (text)", "unit": "-"},
            {"key": "Run_hrs", "question": "Total run hours?", "unit": "hours"},
            {"key": "Mileage", "question": "Mileage (km/l)?", "unit": "km/l"},
            {"key": "Fuel_Con", "question": "Total fuel consumed (litres)?", "unit": "litres"}
        ],
        "operation": "single"   # we'll use Fuel_Con as numeric
    },
    "OVER_B_EM": {
        "fields": [
            {"key": "m3", "question": "Total overburden volume (m3)?", "unit": "m3"},
            {"key": "T", "question": "Total tonnage (T)?", "unit": "T"}
        ],
        "operation": "sum"
    },
    "LMV_EM_D": {
        "fields":[
            {"key":"Model","question":"LMV model (text)","unit":"-"},
            {"key":"Run_hrs","question":"Total run hours?","unit":"hours"},
            {"key":"Mileage","question":"Mileage (km/l)?","unit":"km/l"},
            {"key":"Fuel_Con","question":"Total fuel consumed (litres)?","unit":"litres"}
        ],
        "operation":"single"
    },
    "LMV_EM_G": {
        "fields":[
            {"key":"Fuel_Con","question":"Total gasoline consumed (litres)?","unit":"litres"}
        ],
        "operation":"single"
    },
    "PUMP_DEW_EM": {
        "fields":[
            {"key":"Type","question":"Pump type (text)","unit":"-"},
            {"key":"Model","question":"Pump model (text)","unit":"-"},
            {"key":"Run_Hrs","question":"Total run hours?","unit":"hours"},
            {"key":"Per_hr","question":"Fuel consumption per hour (litres/hr)?","unit":"litres/hr"},
            {"key":"Fuel_cons","question":"Total fuel consumed (litres)? (if known)", "unit":"litres"}
        ],
        "operation":"single"
    },
    "PORT_DG_EM": {
        "fields":[
            {"key":"Type","question":"Portable DG type (text)","unit":"-"},
            {"key":"Model","question":"Portable DG model (text)","unit":"-"},
            {"key":"Run_hr","question":"Run hours?","unit":"hours"},
            {"key":"Per_Hr","question":"Fuel per hour (litres/hr)?","unit":"litres/hr"},
            {"key":"Fuel_Cons","question":"Total fuel consumed (litres)? (if known)","unit":"litres"}
        ],
        "operation":"single"
    },
    "AC_R32_EM": {
        "fields":[
            {"key":"Area","question":"Area served by AC (m2)?","unit":"m2"},
            {"key":"no","question":"Number of AC units?","unit":"Nos"},
            {"key":"Tonnage","question":"Tonnage per AC?","unit":"ton"},
            {"key":"Wattage","question":"Wattage per unit (W)?","unit":"W"},
            {"key":"Run_Time","question":"Daily run time (hours)?","unit":"hours"},
            {"key":"Energy","question":"Total energy consumption (Wh)?","unit":"Wh"},
            {"key":"Leakage","question":"Refrigerant leakage (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "OXY_ACE_EM": {
        "fields":[
            {"key":"Type","question":"Type of oxy-acetylene (text)","unit":"-"},
            {"key":"Weight_cylinder","question":"Weight of cylinder (kg)?","unit":"kg"},
            {"key":"No_of_Cylinder","question":"Number of cylinders?","unit":"Nos"},
            {"key":"Volume_gas_m3","question":"Volume of gas (m3) per cylinder?","unit":"m3"},
            {"key":"Weight_of_gas","question":"Weight of gas per cylinder (kg)?","unit":"kg"},
            {"key":"Total_weight_gas","question":"Total weight of gas (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "DIESEL_DRILL_EM": {
        "fields":[
            {"key":"No_of_Drills","question":"Number of drills?","unit":"Nos"},
            {"key":"Tot_Fuel_cons","question":"Total fuel consumption (litres)?","unit":"litres"}
        ],
        "operation":"single"
    },
    "LUBE_USE_EM": {
        "fields":[
            {"key":"Type","question":"Lubricant type (text)","unit":"-"},
            {"key":"Sub_process","question":"Sub-process name (text)","unit":"-"},
            {"key":"Annual_cons","question":"Annual lubricant consumption (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "ELECT_EM": {
        "fields":[
            {"key":"Type","question":"Electricity type (text)","unit":"-"},
            {"key":"Total_Consumption","question":"Total electricity consumption (kWh)?","unit":"kWh"}
        ],
        "operation":"single"
    },
    "DRILL_BIL_PROD_EM": {
        "fields":[
            {"key":"Type","question":"Drill bit type (text)","unit":"-"},
            {"key":"Weight","question":"Weight per bit (kg)?","unit":"kg"},
            {"key":"No","question":"Number of bits?","unit":"Nos"}
        ],
        "operation":"multiply"
    },
    "LUBE_PROD_EM": {
        "fields":[
            {"key":"Type","question":"Lubricant product type (text)","unit":"-"},
            {"key":"Sub_process","question":"Sub process (text)","unit":"-"},
            {"key":"Annual_cons","question":"Annual consumption (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "PVC_BOX_PROD_EM": {
        "fields":[
            {"key":"Box_type","question":"Box type (text)","unit":"-"},
            {"key":"Total_number","question":"Total number of boxes?","unit":"Nos"},
            {"key":"wt_unit","question":"Weight per box (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "HEMV_TYRE_PROD_EM": {
        "fields":[
            {"key":"No","question":"Number of HEMV tyres?","unit":"Nos"},
            {"key":"Weight","question":"Weight per tyre (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "LMV_TYRE_PROD_EM": {
        "fields":[
            {"key":"No","question":"Number of LMV tyres?","unit":"Nos"},
            {"key":"Weight","question":"Weight per tyre (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "BATT_PROD_EM": {
        "fields":[
            {"key":"Batt_volt","question":"Battery voltage (V)?","unit":"V"},
            {"key":"Batt_cap","question":"Battery capacity (AH)?","unit":"AH"},
            {"key":"No","question":"Number of batteries?","unit":"Nos"},
            {"key":"Model","question":"Battery model (text)","unit":"-"},
            {"key":"Unit_Power_kWh","question":"Unit power (kWh)?","unit":"kWh"}
        ],
        "operation":"single"
    },
    "BLAST_PROD_EM": {
        "fields":[
            {"key":"Type","question":"Explosive type (text)","unit":"-"},
            {"key":"Chem","question":"Chemical used (text)","unit":"-"},
            {"key":"quantity","question":"Quantity used (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "OXY_ACE_PROD_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"Weight_cylinder","question":"Weight of cylinder (kg)?","unit":"kg"},
            {"key":"No_of_Cylinder","question":"Number of cylinders?","unit":"Nos"},
            {"key":"Tot_wt_cyln","question":"Total weight of cylinders (kg)?","unit":"kg"},
            {"key":"Volume_gas_m3","question":"Volume of gas (m3)?","unit":"m3"},
            {"key":"Weight_of_gas","question":"Weight of gas (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "ELECT_ARC_PROD_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"No","question":"Number (Nos)?","unit":"Nos"},
            {"key":"Weight_unit","question":"Weight per unit (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "HDPE5_PROD_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"No","question":"Number of pipes?","unit":"Nos"},
            {"key":"Dia_inch","question":"Diameter (inch)?","unit":"inch"},
            {"key":"Length_m","question":"Length (m)?","unit":"m"}
        ],
        "operation":"single"
    },
    "LPG_PROD_EM": {
        "fields":[
            {"key":"LPG_no","question":"Number of LPG cylinders?","unit":"Nos"},
            {"key":"Weight_LPG","question":"Weight per cylinder (kg)?","unit":"kg"},
            {"key":"Weight_of_Cylinder","question":"Cylinder weight (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "FE_CHROM_PROD_EM": {
        "fields":[
            {"key":"Ore","question":"Ore quantity (kg)?","unit":"kg"},
            {"key":"Ferro_chrome","question":"Ferro chrome produced (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "STEEL_PROD_EM": {
        "fields":[
            {"key":"Ore","question":"Ore quantity (kg)?","unit":"kg"},
            {"key":"Steel","question":"Steel produced (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "WTP_ELECT_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"Amount_WW_KLY","question":"Amount of wastewater (KLY)?","unit":"KLY"},
            {"key":"Energy_per_m3","question":"Energy per m3 (kWh/m3)?","unit":"kWh/m3"}
        ],
        "operation":"single"
    },
    "QC_CHEM_PROD_EM": {
        "fields":[
            {"key":"Chemicals","question":"Name of chemical (text)","unit":"-"},
            {"key":"No_Samples","question":"Number of samples?","unit":"Nos"},
            {"key":"Cons_Six_mnths","question":"Consumption in 6 months (kg)?","unit":"kg"},
            {"key":"Annual_Cons","question":"Annual consumption (kg)?","unit":"kg"},
            {"key":"Unit","question":"Unit (text)","unit":"-"},
            {"key":"m3_Annual_cons_kg","question":"Annual cons (kg)?","unit":"kg"},
            {"key":"EF","question":"Emission factor (kgCO2e/unit)?","unit":"kgCO2e/unit"}
        ],
        "operation":"single"
    },
    "CHEM_ETP_PROD_EM": {
        "fields":[
            {"key":"Chemicals","question":"Chemical name (text)","unit":"-"},
            {"key":"Consumption_kg","question":"Consumption (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "DISP_TYRE_EM": {
        "fields":[
            {"key":"Type","question":"Tyre type (text)","unit":"-"},
            {"key":"No","question":"Number of tyres?","unit":"Nos"},
            {"key":"Weight","question":"Weight per tyre (kg)?","unit":"kg"}
        ],
        "operation":"multiply"
    },
    "DISP_LUBE_EM": {
        "fields":[
            {"key":"Type","question":"Lubricant type (text)","unit":"-"},
            {"key":"Sub_process","question":"Sub process (text)","unit":"-"},
            {"key":"Annual_cons","question":"Annual consumption (kg)?","unit":"kg"}
        ],
        "operation":"single"
    },
    "TRANS_2WHS_EM": {
        "fields":[
            {"key":"No","question":"Number of 2W vehicles?","unit":"Nos"},
            {"key":"Distance_km","question":"Distance travelled (km)?","unit":"km"}
        ],
        "operation":"multiply"
    },
    "TRANS_BUS_EM": {
        "fields":[
            {"key":"No","question":"Number of buses?","unit":"Nos"},
            {"key":"HSD_lts","question":"HSD consumed (litres)?","unit":"litres"},
            {"key":"Distance_km","question":"Distance (km)?","unit":"km"},
            {"key":"Mileage","question":"Mileage (km/l)?","unit":"km/l"}
        ],
        "operation":"single"
    },
    "TRANS_PLANE_EM": {
        "fields":[
            {"key":"Date","question":"Date of travel (YYYY-MM-DD)","unit":"date"},
            {"key":"Place","question":"Destination (text)","unit":"-"},
            {"key":"Pax","question":"Number of passengers?","unit":"Nos"},
            {"key":"Distance","question":"Distance (km)?","unit":"km"}
        ],
        "operation":"single"
    },
    "TRANS_LMV_EM": {
        "fields":[
            {"key":"Date","question":"Date (YYYY-MM-DD)","unit":"date"},
            {"key":"Place","question":"Place (text)","unit":"-"},
            {"key":"Pax","question":"Passengers?","unit":"Nos"},
            {"key":"Distance","question":"Distance (one-way km) - system will use 2*Distance for roundtrip","unit":"km"}
        ],
        "operation":"single"
    },
    "TRANS_6WHS_EM": {
        "fields":[
            {"key":"Client","question":"Client (text)","unit":"-"},
            {"key":"Place","question":"Place (text)","unit":"-"},
            {"key":"No","question":"Number of vehicles?","unit":"Nos"},
            {"key":"Distance","question":"Distance (km)?","unit":"km"}
        ],
        "operation":"single"
    },
    "TRANS_12_14WHS_EM": {
        "fields":[
            {"key":"Client","question":"Client (text)","unit":"-"},
            {"key":"Place","question":"Place (text)","unit":"-"},
            {"key":"Type","question":"Vehicle type (text)","unit":"-"},
            {"key":"No","question":"Number of vehicles?","unit":"Nos"},
            {"key":"Distance","question":"Distance (km)?","unit":"km"}
        ],
        "operation":"single"
    },
    "MIN_QC_TRANS_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"Total_distance","question":"Total distance (km)?","unit":"km"}
        ],
        "operation":"single"
    },
    "CORE_QC_TRANS_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"Total_distance","question":"Total distance (km)?","unit":"km"}
        ],
        "operation":"single"
    },
    "CORE_TRANS_BB_EM": {
        "fields":[
            {"key":"Type","question":"Type (text)","unit":"-"},
            {"key":"Total_distance","question":"Total distance (km)?","unit":"km"}
        ],
        "operation":"single"
    },
    "GEN_ITEM_PROD_EM": {
        "fields":[
            {"key":"Item","question":"Item name (text)","unit":"-"},
            {"key":"Consumption","question":"Consumption (units)?","unit":"units"},
            {"key":"Wt_kg","question":"Weight (kg)?","unit":"kg"},
            {"key":"EF","question":"Emission factor (kgCO2e/unit)?","unit":"kgCO2e/unit"},
            {"key":"unit","question":"Unit (text)","unit":"-"}
        ],
        "operation":"single"
    }
}
