import streamlit as st
import os
import json
from datetime import datetime
import serial
import serial.tools.list_ports

# -------------------------------
# إعداد الحفظ
# -------------------------------
save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "FNS_results")
os.makedirs(save_dir, exist_ok=True)

# -------------------------------
# اللغات
# -------------------------------
lang = st.selectbox("Language / اللغة / Langue", ["English", "العربية", "Français"])

def tr(en, ar, fr):
    if lang == "العربية":
        return ar
    elif lang == "Français":
        return fr
    return en

# -------------------------------
# الاتصال بالجهاز
# -------------------------------
def auto_connect():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        try:
            ser = serial.Serial(port.device, 9600, timeout=2)
            return ser
        except:
            continue
    return None

def read_device():
    ser = auto_connect()
    if ser:
        try:
            raw = ser.read(2048).decode(errors="ignore")
            ser.close()

            data = {}
            for line in raw.split("\n"):
                if ":" in line:
                    k, v = line.split(":")
                    try:
                        data[k.strip()] = float(v.strip())
                    except:
                        pass
            return data
        except:
            return None
    return None

# -------------------------------
# التحليل
# -------------------------------
def analyze(data):
    report = []

    WBC = data.get("WBC",0)
    NEUT = data.get("NEUT",0)
    LYM = data.get("LYM",0)
    MONO = data.get("MONO",0)
    EOS = data.get("EOS",0)
    BASO = data.get("BASO",0)

    RBC = data.get("RBC",0)
    HGB = data.get("HGB",0)
    HCT = data.get("HCT",0)
    MCV = data.get("MCV",0)
    MCH = data.get("MCH",0)
    MCHC = data.get("MCHC",0)

    PLT = data.get("PLT",0)
    FBS = data.get("FBS",0)

    # WBC
    if WBC > 11:
        report.append(tr("High WBC","ارتفاع WBC","WBC élevé"))
        if NEUT > 70:
            report.append(tr("Bacterial infection","عدوى بكتيرية","Infection bactérienne"))
        elif LYM > 40:
            report.append(tr("Viral infection","عدوى فيروسية","Infection virale"))
    elif WBC < 4:
        report.append(tr("Low WBC","انخفاض WBC","WBC faible"))

    # Differential
    if MONO > 10:
        report.append(tr("High Monocytes","ارتفاع MONO","Monocytes élevés"))
    if EOS > 6:
        report.append(tr("Possible allergy/parasite","حساسية أو طفيليات","Allergie ou parasite"))
    if BASO > 2:
        report.append(tr("High Basophils","ارتفاع BASO","Basophiles élevés"))

    # RBC / Anemia
    if HGB < 12:
        if MCV < 80:
            report.append(tr("Iron deficiency anemia","أنيميا نقص الحديد","Anémie ferriprive"))
        elif MCV > 100:
            report.append(tr("B12/Folate deficiency anemia","أنيميا نقص B12","Anémie carence B12"))
        else:
            report.append(tr("Normocytic anemia","أنيميا عادية","Anémie normocytaire"))

    # Platelets
    if PLT < 150:
        report.append(tr("Low platelets","نقص الصفائح","Thrombopénie"))
    elif PLT > 400:
        report.append(tr("High platelets","ارتفاع الصفائح","Thrombocytose"))

    # Sugar
    if FBS > 126:
        report.append(tr("Hyperglycemia","ارتفاع السكر","Hyperglycémie"))
    elif FBS < 70:
        report.append(tr("Hypoglycemia","انخفاض السكر","Hypoglycémie"))

    return report

# -------------------------------
# الحفظ
# -------------------------------
def save(name, pid, data, report):
    file = os.path.join(save_dir, f"{pid}.json")
    with open(file, "w", encoding="utf-8") as f:
        json.dump({"name":name,"id":pid,"data":data,"report":report}, f, indent=4, ensure_ascii=False)
    return file

# -------------------------------
# الواجهة
# -------------------------------
st.title(tr("FNS Analyzer","محلل FNS","Analyseur FNS"))

name = st.text_input(tr("Patient Name","اسم المريض","Nom du patient"))
pid = st.text_input(tr("Patient ID","رقم المريض","ID patient"))

mode = st.radio("Mode", ["Device", "Manual"])

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

    PLT = st.number_input("PLT")
    FBS = st.number_input("FBS")

# -------------------------------
# زر التحليل
# -------------------------------
if st.button("Analyze"):

    if not pid:
        st.warning("Enter patient ID")
    else:
        if mode == "Device":
            data = read_device()
            if not data:
                st.warning("Device not detected, switch to manual")
                data = {}
        else:
            data = {
                "WBC":WBC,"NEUT":NEUT,"LYM":LYM,"MONO":MONO,"EOS":EOS,"BASO":BASO,
                "RBC":RBC,"HGB":HGB,"HCT":HCT,"MCV":MCV,"MCH":MCH,"MCHC":MCHC,
                "PLT":PLT,"FBS":FBS
            }

        report = analyze(data)

        st.write(data)
        for r in report:
            st.write("- "+r)

        save(name, pid, data, report)
        st.success("Saved")
