import streamlit as st
import os
import json
from datetime import datetime
import serial
import serial.tools.list_ports

# -------------------------------
# إعداد مجلد حفظ النتائج
# -------------------------------
save_dir = os.path.join(os.path.expanduser("~"), "Desktop", "FNS_results")
os.makedirs(save_dir, exist_ok=True)

# -------------------------------
# اختيار اللغة
# -------------------------------
lang = st.selectbox("Language / Langue / اللغة", ["English", "Français", "العربية"])
def tr(en, fr, ar):
    if lang=="Français":
        return fr
    elif lang=="العربية":
        return ar
    else:
        return en

# -------------------------------
# دالة تحليل FNS و التشخيص الاحترافي
# -------------------------------
def analyze_fns(data):
    report = []
    WBC = data.get("WBC",0)
    NEUT = data.get("NEUT%",0)
    LYM = data.get("LYMPH%",0)
    HGB = data.get("HGB",0)
    MCV = data.get("MCV",0)
    PLT = data.get("PLT",0)
    FBS = data.get("FBS",0)

    # WBC
    if WBC>11:
        report.append(tr("High WBC - infection/inflammation",
                         "WBC élevé - infection/inflammation",
                         "ارتفاع WBC - عدوى/التهاب"))
        if NEUT>70:
            report.append(tr("Neutrophilia - possible bacterial infection. Recommend CRP, Procalcitonin",
                             "Neutrophilie - possible infection bactérienne. CRP, Procalcitonine recommandés",
                             "ارتفاع العدلات - احتمال عدوى بكتيرية. يُنصح CRP, Procalcitonin"))
        elif LYM>40:
            report.append(tr("Lymphocytosis - possible viral infection",
                             "Lymphocytose - infection virale possible",
                             "ارتفاع اللمفاويات - احتمال عدوى فيروسية"))
    elif WBC<4:
        report.append(tr("Low WBC - viral infection or bone marrow issue",
                         "WBC bas - infection virale ou problème moelle osseuse",
                         "انخفاض WBC - عدوى فيروسية أو نخاع العظم"))

    # HGB و MCV
    if HGB<12:
        if MCV<80:
            report.append(tr("Microcytic anemia - iron deficiency. Recommend Ferritin, Serum Iron",
                             "Anémie microcytaire - carence en fer. Ferritine, Fer sérique recommandés",
                             "أنيميا صغرى - نقص الحديد محتمل. يُنصح Ferritin, Serum Iron"))
        elif MCV>100:
            report.append(tr("Macrocytic anemia - B12 or folate deficiency. Recommend Vitamin B12, Folate",
                             "Anémie macrocytaire - carence B12 ou folate. Vitamine B12, Folate recommandés",
                             "أنيميا كبرى - نقص B12 أو Folate محتمل"))
        else:
            report.append(tr("Normocytic anemia - chronic disease or blood loss",
                             "Anémie normocytaire - maladie chronique ou perte de sang",
                             "أنيميا متوسطة الحجم - مرض مزمن أو فقد دم"))

    # PLT
    if PLT<150:
        report.append(tr("Thrombocytopenia - risk of bleeding",
                         "Thrombocytopénie - risque de saignement",
                         "انخفاض الصفائح - خطر النزيف"))
    elif PLT>400:
        report.append(tr("Thrombocytosis - inflammation or myeloproliferative disorder",
                         "Thrombocytose - inflammation ou trouble myéloprolifératif",
                         "ارتفاع الصفائح - التهاب أو اضطراب نخاعي"))

    # FBS
    if FBS>126:
        report.append(tr("High fasting blood sugar - suggestive of diabetes",
                         "Glycémie à jeun élevée - possible diabète",
                         "ارتفاع السكر الصائم - احتمال السكري"))
    elif FBS<70:
        report.append(tr("Low fasting blood sugar - risk of hypoglycemia",
                         "Glycémie à jeun basse - risque d'hypoglycémie",
                         "انخفاض السكر الصائم - خطر نقص السكر"))

    return report

# -------------------------------
# دالة حفظ النتائج
# -------------------------------
def save_results(name, pid, data, report):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(save_dir,f"{pid}_{name}_{timestamp}.json" if name else f"{pid}_{timestamp}.json")
    to_save = {"patient_name":name,"patient_id":pid,"data":data,"report":report,"timestamp":timestamp}
    with open(filename,"w", encoding="utf-8") as f:
        json.dump(to_save,f,indent=4,ensure_ascii=False)
    return filename

# -------------------------------
# دالة الربط التلقائي مع أي جهاز FNS
# -------------------------------
def auto_connect_fns():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        for baud in [9600, 19200, 38400]:
            try:
                ser = serial.Serial(port.device, baudrate=baud, timeout=2)
                line = ser.readline().decode().strip()
                if any(keyword in line for keyword in ["WBC","RBC","HGB","PLT"]):
                    return ser
            except:
                continue
    return None

# -------------------------------
# دالة قراءة البيانات من الجهاز
# -------------------------------
def read_device_data():
    ser = auto_connect_fns()
    if ser:
        raw_data = ser.read(1024).decode().strip()
        # TODO: هنا نضيف parsing لكل نوع جهاز (ASTM, HL7, TCP)
        # مؤقتاً للتجربة نستخدم بيانات تجريبية
        device_data = {
            "WBC": 12.5, "NEUT%": 75, "LYMPH%": 20,
            "RBC": 4.1, "HGB": 10.8, "HCT": 32,
            "MCV": 78, "MCH": 26, "MCHC":33,
            "PLT":420, "FBS":110
        }
        return device_data
    return None

# -------------------------------
# واجهة المستخدم
# -------------------------------
st.title(tr("FNS Analyzer","Analyseur FNS","محلل FNS"))

patient_name = st.text_input(tr("Patient Name (Optional)","Nom du patient (optionnel)","اسم المريض (اختياري)"))
patient_id = st.text_input(tr("Patient ID","ID du patient","رقم المريض"))

if st.button(tr("Connect & Analyze","Connecter & Analyser","ربط وتحليل")):
    if not patient_id:
        st.warning(tr("Please enter at least the patient ID",
                      "Veuillez entrer au moins l'ID du patient",
                      "رجاء إدخال رقم المريض"))
    else:
        device_data = read_device_data()
        if device_data is None:
            st.error(tr("Device not connected or unrecognized",
                        "Appareil non connecté ou non reconnu",
                        "الجهاز غير متصل أو غير معروف"))
        else:
            report = analyze_fns(device_data)

            st.subheader(tr("FNS Test Results","Résultats FNS","نتائج تحليل FNS"))
            for k,v in device_data.items():
                st.write(f"**{k}**: {v}")

            st.subheader(tr("Interpretation / Recommendations",
                            "Interprétation / Recommandations",
                            "التفسير / التوصيات"))
            for line in report:
                st.write(f"- {line}")

            saved_file = save_results(patient_name,patient_id,device_data,report)
            st.success(tr(f"Results saved in: {saved_file}",
                          f"Résultats sauvegardés dans: {saved_file}",
                          f"تم حفظ النتائج في: {saved_file}"))

            st.markdown(tr("You can now print the page using your browser print option",
                           "Vous pouvez maintenant imprimer la page via l'option d'impression du navigateur",
                           "يمكنك الآن طباعة الصفحة باستخدام خيار الطباعة في المتصفح"))
