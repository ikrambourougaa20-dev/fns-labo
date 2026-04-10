import streamlit as st
import json, os

# -------------------------------
# اللغة
# -------------------------------
lang = st.selectbox("Language / اللغة / Langue", ["English","العربية","Français"])

def tr(en, ar, fr):
    if lang=="العربية": return ar
    if lang=="Français": return fr
    return en

st.title(tr("FNS Smart Analyzer","محلل FNS الذكي","Analyseur FNS Intelligent"))

# -------------------------------
# معلومات المريض
# -------------------------------
name = st.text_input(tr("Patient Name (Optional)","اسم المريض (اختياري)","Nom (optionnel)"))
pid = st.text_input(tr("Patient ID (Required)","رقم المريض (إجباري)","ID patient (obligatoire)"))

# -------------------------------
# الوضع
# -------------------------------
mode = st.radio(tr("Mode","الوضع","Mode"), ["Manual","Device"])

# -------------------------------
# إدخال القيم (Manual)
# -------------------------------
if mode == "Manual":

    st.subheader("WBC")
    WBC = st.number_input("WBC", value=None)
    Lymph = st.number_input("Lymph#", value=None)
    Mid = st.number_input("Mid#", value=None)
    Gran = st.number_input("Gran#", value=None)
    Lymph_p = st.number_input("Lymph%", value=None)
    Mid_p = st.number_input("Mid%", value=None)
    Gran_p = st.number_input("Gran%", value=None)

    st.subheader("RBC")
    RBC = st.number_input("RBC", value=None)
    HGB = st.number_input("HGB", value=None)
    HCT = st.number_input("HCT", value=None)
    MCV = st.number_input("MCV", value=None)
    MCH = st.number_input("MCH", value=None)
    MCHC = st.number_input("MCHC", value=None)
    RDW_CV = st.number_input("RDW-CV", value=None)
    RDW_SD = st.number_input("RDW-SD", value=None)

    st.subheader("Platelets")
    PLT = st.number_input("PLT", value=None)
    MPV = st.number_input("MPV", value=None)
    PDW = st.number_input("PDW", value=None)
    PCT = st.number_input("PCT", value=None)
    PLCC = st.number_input("P-LCC", value=None)
    PLCR = st.number_input("P-LCR", value=None)

# -------------------------------
# Validation
# -------------------------------
def validate(data):
    errors = []
    for k,v in data.items():
        if v is not None and v < 0:
            errors.append(tr(f"{k} invalid value","قيمة غير صالحة","valeur invalide"))
    return errors

# -------------------------------
# Consistency
# -------------------------------
def consistency(data):
    warn = []
    if data.get("HGB") and data.get("HCT"):
        if abs(data["HCT"] - 3*data["HGB"]) > 5:
            warn.append(tr("HCT not consistent with HGB",
                           "HCT غير متوافق مع HGB",
                           "HCT incohérent avec HGB"))
    return warn

# -------------------------------
# Auto calc
# -------------------------------
def auto_calc(data):
    if data.get("Gran%") and data.get("Lymph%") and not data.get("Mid%"):
        data["Mid%"] = 100 - (data["Gran%"] + data["Lymph%"])
    return data

# -------------------------------
# Low / High
# -------------------------------
ranges = {
    "WBC":(4,11),
    "HGB":(12,16),
    "PLT":(150,400)
}

# -------------------------------
# التشخيص (فقرة مفهومة)
# -------------------------------
def diagnosis_text(data):

    text = ""

    WBC = data.get("WBC")
    Gran = data.get("Gran#")
    Lymph = data.get("Lymph#")
    HGB = data.get("HGB")
    MCV = data.get("MCV")

    # Infection
    if WBC:
        if WBC > 11:
            if Gran and Lymph and Gran > Lymph:
                text += tr("Elevated white blood cells suggest a bacterial infection. ",
                           "ارتفاع كريات الدم البيضاء يشير إلى احتمال وجود عدوى بكتيرية. ",
                           "L'augmentation des globules blancs suggère une infection bactérienne. ")
            elif Lymph and Gran and Lymph > Gran:
                text += tr("Elevated white blood cells suggest a viral infection. ",
                           "ارتفاع كريات الدم البيضاء يشير إلى احتمال وجود عدوى فيروسية. ",
                           "L'augmentation des globules blancs suggère une infection virale. ")

    # Anemia
    if HGB:
        if HGB < 12:
            if MCV and MCV < 80:
                text += tr("Low hemoglobin with low MCV indicates iron deficiency anemia. ",
                           "انخفاض الهيموغلوبين مع MCV منخفض يدل على أنيميا نقص الحديد. ",
                           "Hémoglobine basse avec MCV bas indique une anémie ferriprive. ")
            elif MCV and MCV > 100:
                text += tr("Findings suggest vitamin B12 deficiency anemia. ",
                           "النتائج تشير إلى أنيميا نقص فيتامين B12. ",
                           "Les résultats suggèrent une anémie par déficit en B12. ")
            else:
                text += tr("Mild anemia detected. ",
                           "يوجد فقر دم بسيط. ",
                           "Anémie légère détectée. ")

    return text

# -------------------------------
# زر التحليل
# -------------------------------
if st.button(tr("Analyze","تحليل","Analyser")):

    if not pid:
        st.error(tr("Enter Patient ID","أدخل رقم المريض","Entrez ID patient"))

    else:
        data = {
            "WBC":WBC,"Lymph#":Lymph,"Mid#":Mid,"Gran#":Gran,
            "Lymph%":Lymph_p,"Mid%":Mid_p,"Gran%":Gran_p,
            "RBC":RBC,"HGB":HGB,"HCT":HCT,"MCV":MCV,
            "MCH":MCH,"MCHC":MCHC,"RDW-CV":RDW_CV,"RDW-SD":RDW_SD,
            "PLT":PLT,"MPV":MPV,"PDW":PDW,"PCT":PCT,
            "P-LCC":PLCC,"P-LCR":PLCR
        }

        data = auto_calc(data)

        errors = validate(data)
        warns = consistency(data)

        st.subheader(tr("Results","النتائج","Résultats"))
        st.write(data)

        # Low / High
        for k,v in data.items():
            if k in ranges and v:
                low,high = ranges[k]
                if v < low:
                    st.error(f"{k} LOW")
                elif v > high:
                    st.warning(f"{k} HIGH")

        st.subheader(tr("Diagnosis","التشخيص","Diagnostic"))
        st.write(diagnosis_text(data))

        st.subheader(tr("Warnings","تحذيرات","Avertissements"))
        for w in warns:
            st.warning(w)

        for e in errors:
            st.error(e)

        # -------------------------------
        # حفظ وطباعة
        # -------------------------------
        if st.button(tr("Save Report","حفظ التقرير","Enregistrer")):
            with open(f"{pid}.json","w") as f:
                json.dump(data,f)
            st.success(tr("Saved successfully","تم الحفظ","Enregistré"))

        st.markdown("""
        <script>
        function printPage() { window.print(); }
        </script>
        <button onclick="printPage()">🖨️ Print</button>
        """, unsafe_allow_html=True)
