import streamlit as st
import os, json
from datetime import datetime
import serial
import serial.tools.list_ports

# -------------------------------
# إعداد الحفظ
# -------------------------------
save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "FNS_results")
os.makedirs(save_dir, exist_ok=True)

# -------------------------------
# اختيار اللغة
# -------------------------------
lang = st.selectbox("Language / اللغة / Langue", ["English", "العربية", "Français"])

def tr(en, ar, fr):
    if lang == "العربية": return ar
    if lang == "Français": return fr
    return en

# -------------------------------
# الواجهة الرئيسية
# -------------------------------
st.title(tr("FNS Smart Analyzer","محلل FNS الذكي","Analyseur FNS intelligent"))

# اسم + رقم
name = st.text_input(tr("Patient Name (Optional)",
                        "اسم المريض (اختياري)",
                        "Nom du patient (optionnel)"))

pid = st.text_input(tr("Patient ID (Required)",
                       "رقم المريض (إجباري)",
                       "ID patient (obligatoire)"))

# اختيار الوضع
mode = st.radio(tr("Mode","الوضع","Mode"),
                ["Manual","Device"])

# -------------------------------
# إدخال يدوي (بدون 0)
# -------------------------------
def num(label):
    return st.number_input(label, value=None, placeholder="")

if mode == "Manual":
    st.subheader("FNS Inputs")

    WBC = num("WBC")
    NEUT = num("NEUT%")
    LYM = num("LYM%")
    MONO = num("MONO%")
    EOS = num("EOS%")
    BASO = num("BASO%")

    RBC = num("RBC")
    HGB = num("HGB")
    HCT = num("HCT")
    MCV = num("MCV")
    MCH = num("MCH")
    MCHC = num("MCHC")
    RDW = num("RDW")

    PLT = num("PLT")
    MPV = num("MPV")
    PDW = num("PDW")

    FBS = num("FBS")

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
# Validation
# -------------------------------
def validate(data):
    errors = []
    for k,v in data.items():
        if v is not None and v < 0:
            errors.append(f"{k} invalid")
    return errors

# -------------------------------
# Consistency
# -------------------------------
def consistency(data):
    warnings = []
    if data.get("HGB") and data.get("HCT"):
        if abs(data["HCT"] - 3*data["HGB"]) > 5:
            warnings.append("HCT inconsistent with HGB")
    return warnings

# -------------------------------
# Auto calc
# -------------------------------
def auto_calc(data):
    if data.get("NEUT") and data.get("LYM") and not data.get("MONO"):
        data["MONO"] = 100 - (data["NEUT"] + data["LYM"])
    return data

# -------------------------------
# Normalization
# -------------------------------
def normalize(data):
    mapping = {"NEUT%":"NEUT","LYMPH%":"LYM"}
    return {mapping.get(k,k):v for k,v in data.items()}

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

    if WBC and WBC > 11:
        if NEUT and NEUT > 70:
            report.append("Bacterial infection suspected")
            suggestions.append("CRP, Procalcitonin")
        elif LYM and LYM > 40:
            report.append("Viral infection suspected")

    if HGB and HGB < 12:
        if MCV and MCV < 80:
            report.append("Iron deficiency anemia")
            suggestions.append("Ferritin")
        elif MCV and MCV > 100:
            report.append("B12 deficiency anemia")

    if PLT:
        if PLT < 150:
            alerts.append("Bleeding risk")
        elif PLT > 400:
            report.append("Inflammation")

    if FBS:
        if FBS > 126:
            alerts.append("Diabetes suspected")
        elif FBS < 70:
            alerts.append("Hypoglycemia")

    return report, suggestions, alerts

# -------------------------------
# زر التحليل
# -------------------------------
if st.button(tr("Analyze","تحليل","Analyser")):

    if not pid:
        st.error(tr("Patient ID required","رقم المريض إجباري","ID obligatoire"))
    else:
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

        data = normalize(data)
        data = auto_calc(data)

        errors = validate(data)
        warnings = consistency(data)

        report, suggestions, alerts = analyze(data)

        # -----------------------
        # عرض النتائج
        # -----------------------
        st.subheader("Results")
        st.write(data)

        # LOW / HIGH
        for k,v in data.items():
            if v is not None:
                if k=="HGB" and v<12:
                    st.error(f"{k} LOW")
                if k=="WBC" and v>11:
                    st.warning(f"{k} HIGH")

        st.subheader("Diagnosis")
        for r in report:
            st.write("- "+r)

        st.subheader("Suggested Tests")
        for s in suggestions:
            st.write("- "+s)

        st.subheader("Alerts")
        for a in alerts:
            st.error(a)

        for e in errors:
            st.error(e)

        for w in warnings:
            st.warning(w)
