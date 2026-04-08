import streamlit as st
import os, json
from datetime import datetime

# -------------------------------
# إعداد
# -------------------------------
save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "FNS_results")
os.makedirs(save_dir, exist_ok=True)

# -------------------------------
# لغة
# -------------------------------
lang = st.selectbox("Language", ["English", "العربية", "Français"])

def tr(en, ar, fr):
    if lang=="العربية": return ar
    if lang=="Français": return fr
    return en

# -------------------------------
# القيم الطبيعية
# -------------------------------
ranges = {
    "WBC": (4,11),
    "HGB": (12,16),
    "PLT": (150,400),
    "MCV": (80,100),
    "FBS": (70,126)
}

# -------------------------------
# Validation
# -------------------------------
def validate(data):
    warnings = []
    for k,v in data.items():
        if v is None:
            continue
        if v < 0:
            warnings.append(f"{k} invalid")
    return warnings

# -------------------------------
# Consistency
# -------------------------------
def consistency(data):
    alerts = []
    HGB = data.get("HGB")
    HCT = data.get("HCT")

    if HGB and HCT:
        if abs(HCT - 3*HGB) > 5:
            alerts.append("HCT not consistent with HGB")

    return alerts

# -------------------------------
# Auto calculation
# -------------------------------
def auto_calc(data):
    NEUT = data.get("NEUT")
    LYM = data.get("LYM")
    MONO = data.get("MONO")

    if NEUT and LYM and not MONO:
        data["MONO"] = 100 - (NEUT + LYM)

    return data

# -------------------------------
# Normalization
# -------------------------------
def normalize(data):
    mapping = {
        "NEUT%":"NEUT",
        "LYMPH%":"LYM"
    }
    new_data = {}
    for k,v in data.items():
        new_key = mapping.get(k,k)
        new_data[new_key]=v
    return new_data

# -------------------------------
# تحليل
# -------------------------------
def analyze(data):
    report = []
    alerts = []

    WBC = data.get("WBC")
    NEUT = data.get("NEUT")
    LYM = data.get("LYM")
    HGB = data.get("HGB")
    MCV = data.get("MCV")
    PLT = data.get("PLT")
    FBS = data.get("FBS")

    # WBC
    if WBC:
        if WBC > 11:
            if NEUT and NEUT > 70:
                report.append("Bacterial infection suspected")
            elif LYM and LYM > 40:
                report.append("Viral infection suspected")

    # Anemia
    if HGB and HGB < 12:
        if MCV and MCV < 80:
            report.append("Iron deficiency anemia")
        elif MCV and MCV > 100:
            report.append("B12 deficiency anemia")

    # Platelets
    if PLT:
        if PLT < 150:
            alerts.append("Risk of bleeding")
        elif PLT > 400:
            report.append("Possible inflammation")

    # Sugar
    if FBS:
        if FBS > 126:
            alerts.append("Hyperglycemia")
        elif FBS < 70:
            alerts.append("Hypoglycemia")

    return report, alerts

# -------------------------------
# واجهة
# -------------------------------
st.title("FNS Analyzer")

pid = st.text_input("Patient ID")

WBC = st.number_input("WBC", value=None)
NEUT = st.number_input("NEUT%", value=None)
LYM = st.number_input("LYM%", value=None)
HGB = st.number_input("HGB", value=None)
HCT = st.number_input("HCT", value=None)
MCV = st.number_input("MCV", value=None)
PLT = st.number_input("PLT", value=None)
FBS = st.number_input("FBS", value=None)

if st.button("Analyze"):

    data = {
        "WBC":WBC,"NEUT":NEUT,"LYM":LYM,
        "HGB":HGB,"HCT":HCT,"MCV":MCV,
        "PLT":PLT,"FBS":FBS
    }

    data = normalize(data)
    data = auto_calc(data)

    val_warn = validate(data)
    cons_warn = consistency(data)

    report, alerts = analyze(data)

    st.subheader("Results")
    st.write(data)

    # عرض Low / High
    for k,v in data.items():
        if k in ranges and v:
            low,high = ranges[k]
            if v < low:
                st.error(f"{k} LOW")
            elif v > high:
                st.warning(f"{k} HIGH")

    st.subheader("Interpretation")
    for r in report:
        st.write("- "+r)

    st.subheader("Alerts")
    for a in alerts:
        st.error(a)

    for w in val_warn + cons_warn:
        st.warning(w)
