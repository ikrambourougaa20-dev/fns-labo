import streamlit as st
import os
import json
from datetime import datetime

# -------------------------------
# إعداد مجلد الحفظ
# -------------------------------
save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "FNS_results")
os.makedirs(save_dir, exist_ok=True)

# -------------------------------
# اختيار اللغة
# -------------------------------
lang = st.selectbox("Language / اللغة / Langue", ["English", "العربية", "Français"])

def tr(en, ar, fr):
    if lang == "العربية":
        return ar
    elif lang == "Français":
        return fr
    return en

# -------------------------------
# تحليل FNS
# -------------------------------
def analyze_fns(data):
    report = []

    WBC = data["WBC"]
    NEUT = data["NEUT"]
    LYM = data["LYM"]
    HGB = data["HGB"]
    MCV = data["MCV"]
    PLT = data["PLT"]
    FBS = data["FBS"]

    # WBC
    if WBC > 11:
        report.append(tr("High WBC - infection/inflammation",
                         "ارتفاع WBC - عدوى/التهاب",
                         "WBC élevé - infection/inflammation"))
        if NEUT > 70:
            report.append(tr("Possible bacterial infection",
                             "احتمال عدوى بكتيرية",
                             "Infection bactérienne probable"))
        elif LYM > 40:
            report.append(tr("Possible viral infection",
                             "احتمال عدوى فيروسية",
                             "Infection virale probable"))

    elif WBC < 4:
        report.append(tr("Low WBC",
                         "انخفاض WBC",
                         "WBC faible"))

    # Anemia
    if HGB < 12:
        if MCV < 80:
            report.append(tr("Iron deficiency anemia",
                             "أنيميا نقص الحديد",
                             "Anémie ferriprive"))
        elif MCV > 100:
            report.append(tr("B12 deficiency anemia",
                             "أنيميا نقص B12",
                             "Anémie par carence en B12"))
        else:
            report.append(tr("Normocytic anemia",
                             "أنيميا متوسطة",
                             "Anémie normocytaire"))

    # Platelets
    if PLT < 150:
        report.append(tr("Low platelets",
                         "نقص الصفائح",
                         "Thrombopénie"))
    elif PLT > 400:
        report.append(tr("High platelets",
                         "ارتفاع الصفائح",
                         "Thrombocytose"))

    # FBS
    if FBS > 126:
        report.append(tr("High blood sugar",
                         "ارتفاع السكر",
                         "Hyperglycémie"))
    elif FBS < 70:
        report.append(tr("Low blood sugar",
                         "انخفاض السكر",
                         "Hypoglycémie"))

    return report

# -------------------------------
# الحفظ
# -------------------------------
def save_results(name, pid, data, report):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir, f"{pid}_{timestamp}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump({
            "patient_name": name,
            "patient_id": pid,
            "data": data,
            "report": report
        }, f, indent=4, ensure_ascii=False)

    return filename

# -------------------------------
# الواجهة
# -------------------------------
st.title(tr("FNS Analyzer", "محلل FNS", "Analyseur FNS"))

patient_name = st.text_input(tr("Patient Name (Optional)",
                                "اسم المريض (اختياري)",
                                "Nom du patient (optionnel)"))

patient_id = st.text_input(tr("Patient ID",
                              "رقم المريض",
                              "ID du patient"))

# إدخال يدوي
WBC = st.number_input("WBC", 0.0)
NEUT = st.number_input("NEUT%", 0.0)
LYM = st.number_input("LYM%", 0.0)
HGB = st.number_input("HGB", 0.0)
MCV = st.number_input("MCV", 0.0)
PLT = st.number_input("PLT", 0.0)
FBS = st.number_input("FBS", 0.0)

# زر التحليل
if st.button(tr("Analyze", "تحليل", "Analyser")):

    if not patient_id:
        st.warning(tr("Enter patient ID",
                      "أدخل رقم المريض",
                      "Entrez l'ID du patient"))
    else:
        data = {
            "WBC": WBC,
            "NEUT": NEUT,
            "LYM": LYM,
            "HGB": HGB,
            "MCV": MCV,
            "PLT": PLT,
            "FBS": FBS
        }

        report = analyze_fns(data)

        st.subheader(tr("Results", "النتائج", "Résultats"))
        st.write(data)

        st.subheader(tr("Interpretation", "التفسير", "Interprétation"))
        for r in report:
            st.write("- " + r)

        file = save_results(patient_name, patient_id, data, report)

        st.success(tr("Saved successfully",
                      "تم الحفظ بنجاح",
                      "Enregistré avec succès"))

        st.download_button(
            "Download JSON",
            data=json.dumps(data, indent=4),
            file_name="report.json"
        )

        st.markdown(tr("Use browser print to print",
                       "استعمل الطباعة من المتصفح",
                       "Utilisez l'impression du navigateur"))
