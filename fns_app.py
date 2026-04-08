import streamlit as st
import os, json
from datetime import datetime
import serial
import serial.tools.list_ports

# -------------------------------
# إعداد
# -------------------------------
save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "FNS_results")
os.makedirs(save_dir, exist_ok=True)

st.title("FNS Smart Analyzer")

# -------------------------------
# اختيار الوضع
# -------------------------------
mode = st.radio("Mode", ["Device", "Manual"])

pid = st.text_input("Patient ID")

# -------------------------------
# قراءة الجهاز
# -------------------------------
def read_device():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, 9600, timeout=2)
            raw = ser.read(2048).decode(errors="ignore")
            ser.close()

            data = {}
            for line in raw.split("\n"):
                if ":" in line:
                    k,v = line.split(":")
                    try:
                        data[k.strip()] = float(v.strip())
                    except:
                        pass
            return data
        except:
            continue
    return None

# -------------------------------
# إدخال يدوي كامل
# -------------------------------
if mode == "Manual":
    WBC = st.number_input("WBC")
    NEUT = st.number_input("NEUT%")
    LYM = st.number_input("LYM%")
    MONO = st.number_input("MONO%")
    EOS = st.number_input("EOS%")
    BASO = st.number_input("BASO%")

    RBC = st.number_input("RBC")
    HGB = st.number_input("HGB")
    HCT = st.number_input("HCT")
    MCV = st.number_input("MCV")
    MCH = st.number_input("MCH")
    MCHC = st.number_input("MCHC")
    RDW = st.number_input("RDW")

    PLT = st.number_input("PLT")
    MPV = st.number_input("MPV")
    PDW = st.number_input("PDW")

    FBS = st.number_input("FBS")

# -------------------------------
# Validation
# -------------------------------
def validate(data):
    errors = []
    for k,v in data.items():
        if v is not None and v < 0:
            errors.append(f"{k} invalid value")
    return errors

# -------------------------------
# Consistency
# -------------------------------
def consistency(data):
    warnings = []
    if data.get("HGB") and data.get("HCT"):
        if abs(data["HCT"] - 3*data["HGB"]) > 5:
            warnings.append("HCT not consistent with HGB")
    return warnings

# -------------------------------
# Auto calc
# -------------------------------
def auto_calc(data):
    if data.get("NEUT") and data.get("LYM") and not data.get("MONO"):
        data["MONO"] = 100 - (data["NEUT"] + data["LYM"])
    return data

# -------------------------------
# تحليل طبي
# -------------------------------
def analyze(data):
    report = []
    suggestions = []
    alerts = []

    WBC = data.get("WBC")
    NEUT = data.get("NEUT")
    LYM = data.get("LYM")
    HGB = data.get("HGB")
    MCV = data.get("MCV")
    PLT = data.get("PLT")
    FBS = data.get("FBS")

    # Infection
    if WBC and WBC > 11:
        if NEUT and NEUT > 70:
            report.append("Bacterial infection suspected")
            suggestions.append("CRP, Procalcitonin")
        elif LYM and LYM > 40:
            report.append("Viral infection suspected")

    # Anemia
    if HGB and HGB < 12:
        if MCV and MCV < 80:
            report.append("Iron deficiency anemia")
            suggestions.append("Ferritin, Serum Iron")
        elif MCV and MCV > 100:
            report.append("B12 deficiency anemia")
            suggestions.append("Vitamin B12")

    # Platelets
    if PLT:
        if PLT < 150:
            alerts.append("Risk of bleeding")
        elif PLT > 400:
            report.append("Possible inflammation")

    # Sugar
    if FBS:
        if FBS > 126:
            alerts.append("Diabetes suspected")
        elif FBS < 70:
            alerts.append("Hypoglycemia risk")

    return report, suggestions, alerts

# -------------------------------
# زر التحليل
# -------------------------------
if st.button("Analyze"):

    if mode == "Device":
        data = read_device()
        if not data:
            st.warning("Device not detected")
            data = {}
    else:
        data = {
            "WBC":WBC,"NEUT":NEUT,"LYM":LYM,"MONO":MONO,"EOS":EOS,"BASO":BASO,
            "RBC":RBC,"HGB":HGB,"HCT":HCT,"MCV":MCV,"MCH":MCH,"MCHC":MCHC,"RDW":RDW,
            "PLT":PLT,"MPV":MPV,"PDW":PDW,"FBS":FBS
        }

    data = auto_calc(data)

    errors = validate(data)
    warnings = consistency(data)

    report, suggestions, alerts = analyze(data)

    st.subheader("Results")
    st.write(data)

    st.subheader("Diagnosis")
    for r in report:
        st.write("- " + r)

    st.subheader("Suggested Tests")
    for s in suggestions:
        st.write("- " + s)

    st.subheader("Alerts")
    for a in alerts:
        st.error(a)

    for e in errors:
        st.error(e)

    for w in warnings:
        st.warning(w)
