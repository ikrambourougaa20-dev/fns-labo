import streamlit as st
import json
from datetime import datetime

# -----------------------
# Language system
# -----------------------
lang = st.selectbox("Language / اللغة / Langue", ["English", "Français", "العربية"])

def tr(en, fr, ar):
    if lang == "Français": return fr
    if lang == "العربية": return ar
    return en

# -----------------------
# Patient Info
# -----------------------
st.title(tr("FNS Analyzer","Analyseur FNS","محلل FNS"))

patient_name = st.text_input(tr("Patient Name (Optional)","Nom du patient (optionnel)","اسم المريض (اختياري)"))
patient_id = st.text_input(tr("Patient ID (Required)","ID patient (obligatoire)","رقم المريض (إجباري)"))

gender = st.selectbox(tr("Gender","Sexe","الجنس"),
                      [tr("Male","Homme","ذكر"), tr("Female","Femme","أنثى")])

# -----------------------
# Mode selection
# -----------------------
mode = st.radio(tr("Data Source","Source des données","مصدر البيانات"),
                [tr("Manual Input","Saisie manuelle","إدخال يدوي"),
                 tr("Device (Auto)","Appareil (Auto)","جهاز تلقائي")])

# -----------------------
# Input Data
# -----------------------
data = {}

if mode == tr("Manual Input","Saisie manuelle","إدخال يدوي"):
    st.subheader(tr("Enter FNS Values","Entrer les valeurs","ادخل القيم"))
    
    data["WBC"] = st.number_input("WBC", min_value=0.0)
    data["NEUT"] = st.number_input("NEUT%", min_value=0.0)
    data["LYM"] = st.number_input("LYM%", min_value=0.0)
    data["RBC"] = st.number_input("RBC", min_value=0.0)
    data["HGB"] = st.number_input("HGB", min_value=0.0)
    data["HCT"] = st.number_input("HCT", min_value=0.0)
    data["MCV"] = st.number_input("MCV", min_value=0.0)
    data["MCH"] = st.number_input("MCH", min_value=0.0)
    data["MCHC"] = st.number_input("MCHC", min_value=0.0)
    data["PLT"] = st.number_input("PLT", min_value=0.0)
    data["RDW"] = st.number_input("RDW", min_value=0.0)
    data["MPV"] = st.number_input("MPV", min_value=0.0)
    data["PDW"] = st.number_input("PDW", min_value=0.0)

else:
    # Simulated device data
    data = {
        "WBC": 12.5, "NEUT": 75, "LYM": 20,
        "RBC": 4.5, "HGB": 11.2, "HCT": 34,
        "MCV": 78, "MCH": 26, "MCHC": 32,
        "PLT": 420, "RDW": 15, "MPV": 9, "PDW": 13
    }
    st.info(tr("Data loaded from device","Données chargées depuis l'appareil","تم جلب البيانات من الجهاز"))

# -----------------------
# Validation + Logic
# -----------------------
def analyze(data, gender):
    report = []

    WBC = data.get("WBC")
    HGB = data.get("HGB")
    MCV = data.get("MCV")
    PLT = data.get("PLT")

    # Validation
    if WBC and (WBC < 1 or WBC > 100):
        report.append(tr("Abnormal WBC value","Valeur WBC anormale","قيمة WBC غير منطقية"))

    # Gender-based HGB
    if gender.startswith("M"):
        low_hgb = 13
    else:
        low_hgb = 12

    # Diagnosis
    if WBC:
        if WBC > 11:
            report.append(tr("High WBC → possible infection","WBC élevé → infection possible","ارتفاع WBC → احتمال عدوى"))
        elif WBC < 4:
            report.append(tr("Low WBC → immune issue","WBC bas → مشكلة مناعية","انخفاض WBC → مشكلة مناعية"))

    if HGB:
        if HGB < low_hgb:
            if MCV and MCV < 80:
                report.append(tr("Iron deficiency anemia","Anémie ferriprive","أنيميا نقص الحديد"))
            elif MCV and MCV > 100:
                report.append(tr("B12 deficiency anemia","Anémie B12","أنيميا نقص B12"))
            else:
                report.append(tr("Anemia detected","Anémie détectée","تم اكتشاف أنيميا"))

    if PLT:
        if PLT < 150:
            report.append(tr("Low platelets","Plaquettes basses","نقص الصفائح"))
        elif PLT > 400:
            report.append(tr("High platelets","Plaquettes élevées","ارتفاع الصفائح"))

    return report

# -----------------------
# Analyze Button
# -----------------------
if st.button(tr("Analyze","Analyser","تحليل")):
    if not patient_id:
        st.warning(tr("Patient ID required","ID obligatoire","رقم المريض إجباري"))
    else:
        result = analyze(data, gender)

        st.subheader(tr("Results","Résultats","النتائج"))
        for k,v in data.items():
            st.write(f"{k}: {v}")

        st.subheader(tr("Diagnosis","Diagnostic","التشخيص"))
        st.write("\n".join(result))

        # Save
        filename = f"{patient_id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, "w") as f:
            json.dump(data, f)

        st.success(tr("Saved successfully","Enregistré","تم الحفظ"))

        st.button(tr("Print","Imprimer","طباعة"))

