"""All user-facing text. Hindi/Kannada MUST be reviewed by a native speaker before launch."""
L = ("en", "hi", "kn")
def t(en, hi, kn): return {"en": en, "hi": hi, "kn": kn}

YES = t("Yes", "हाँ", "ಹೌದು"); NO = t("No", "नहीं", "ಇಲ್ಲ"); DK = t("Not sure", "पता नहीं", "ಗೊತ್ತಿಲ್ಲ")
def o(v, label): return {"v": v, "label": label}
YN = [o("yes", YES), o("no", NO)]

QUESTIONS = [
 {"id": "q1", "text": t("How old are you?", "आपकी उम्र क्या है?", "ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?"),
  "options": [o("under25", t("Under 25", "25 से कम", "25ಕ್ಕಿಂತ ಕಡಿಮೆ")), o("25_35", t("25 to 35", "25 से 35", "25 ರಿಂದ 35")), o("over35", t("Over 35", "35 से ज़्यादा", "35ಕ್ಕಿಂತ ಹೆಚ್ಚು"))]},
 {"id": "q2", "text": t("Has a doctor told you to remove your womb?", "क्या डॉक्टर ने आपको बच्चेदानी निकालने को कहा है?", "ವೈದ್ಯರು ನಿಮ್ಮ ಗರ್ಭಕೋಶ ತೆಗೆಸಲು ಹೇಳಿದ್ದಾರೆಯೇ?"), "options": YN},
 {"id": "q3", "text": t("What reason did the doctor give?", "डॉक्टर ने क्या कारण बताया?", "ವೈದ್ಯರು ಯಾವ ಕಾರಣ ಹೇಳಿದರು?"),
  "options": [o("pain", t("Pain", "दर्द", "ನೋವು")), o("bleeding", t("Heavy bleeding", "ज़्यादा ब्लीडिंग", "ಹೆಚ್ಚು ರಕ್ತಸ್ರಾವ")),
              o("growth", t("A growth or fibroid", "गांठ या फाइब्रॉइड", "ಗೆಡ್ಡೆ ಅಥವಾ ಫೈಬ್ರಾಯ್ಡ್")), o("none", t("No clear reason", "कोई साफ़ कारण नहीं", "ಸ್ಪಷ್ಟ ಕಾರಣ ಇಲ್ಲ")), o("dk", DK)]},
 {"id": "q4", "text": t("Has a second doctor also advised it?", "क्या किसी दूसरे डॉक्टर ने भी यही सलाह दी?", "ಇನ್ನೊಬ್ಬ ವೈದ್ಯರೂ ಇದೇ ಸಲಹೆ ನೀಡಿದ್ದಾರೆಯೇ?"), "options": YN + [o("dk", DK)]},
 {"id": "q5", "text": t("Is anyone pushing you to do it, like family, employer or contractor?", "क्या कोई आप पर दबाव डाल रहा है, जैसे परिवार, मालिक या ठेकेदार?", "ಕುಟುಂಬ, ಮಾಲೀಕ ಅಥವಾ ಗುತ್ತಿಗೆದಾರರಂತಹ ಯಾರಾದರೂ ನಿಮ್ಮ ಮೇಲೆ ಒತ್ತಡ ಹಾಕುತ್ತಿದ್ದಾರೆಯೇ?"), "options": YN},
 {"id": "q6", "text": t("Do you feel free to say no?", "क्या आप ‘ना’ कहने के लिए आज़ाद महसूस करती हैं?", "‘ಇಲ್ಲ’ ಎಂದು ಹೇಳಲು ನಿಮಗೆ ಸ್ವಾತಂತ್ರ್ಯವಿದೆಯೇ?"), "options": YN},
]

HEADLINE = t("Get a second opinion first.", "पहले दूसरी राय लीजिए।", "ಮೊದಲು ಎರಡನೇ ಅಭಿಪ್ರಾಯ ಪಡೆಯಿರಿ.")
NOTE = t("This is not a medical diagnosis. It is a reminder to ask once more before a big decision.",
         "यह कोई मेडिकल जांच नहीं है। बड़े फ़ैसले से पहले एक बार और पूछने की याद है।",
         "ಇದು ವೈದ್ಯಕೀಯ ರೋಗನಿರ್ಣಯ ಅಲ್ಲ. ದೊಡ್ಡ ನಿರ್ಧಾರದ ಮೊದಲು ಇನ್ನೊಮ್ಮೆ ಕೇಳುವ ನೆನಪು.")
NOT_ADVISED = t("No surgery has been advised. If a doctor ever advises it, ask once more before deciding.",
                "अभी सर्जरी की सलाह नहीं दी गई है। अगर कभी दी जाए, तो फ़ैसले से पहले एक बार और पूछिए।",
                "ಈಗ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಯ ಸಲಹೆ ನೀಡಲಾಗಿಲ್ಲ. ಎಂದಾದರೂ ನೀಡಿದರೆ, ನಿರ್ಧರಿಸುವ ಮೊದಲು ಇನ್ನೊಮ್ಮೆ ಕೇಳಿ.")
DOCTOR_QUESTIONS = [
 t("What exactly is the problem, and how do you know?", "असल में क्या समस्या है, और आपको कैसे पता चला?", "ನಿಜವಾದ ಸಮಸ್ಯೆ ಏನು, ನಿಮಗೆ ಹೇಗೆ ತಿಳಿಯಿತು?"),
 t("Are there treatments other than removing the womb?", "क्या बच्चेदानी निकालने के अलावा कोई इलाज है?", "ಗರ್ಭಕೋಶ ತೆಗೆಯುವುದನ್ನು ಬಿಟ್ಟು ಬೇರೆ ಚಿಕಿತ್ಸೆ ಇದೆಯೇ?"),
 t("What happens if I wait or take other treatment first?", "अगर मैं इंतज़ार करूँ या पहले दूसरा इलाज लूँ तो क्या होगा?", "ನಾನು ಕಾಯ್ದರೆ ಅಥವಾ ಮೊದಲು ಬೇರೆ ಚಿಕಿತ್ಸೆ ಪಡೆದರೆ ಏನಾಗುತ್ತದೆ?"),
 t("What are the risks and side effects of this surgery?", "इस ऑपरेशन के जोखिम और साइड इफेक्ट क्या हैं?", "ಈ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಯ ಅಪಾಯ ಮತ್ತು ಅಡ್ಡಪರಿಣಾಮಗಳು ಏನು?"),
 t("Can you write down the reason in my papers?", "क्या आप कारण मेरे कागज़ों में लिख सकते हैं?", "ಕಾರಣವನ್ನು ನನ್ನ ದಾಖಲೆಗಳಲ್ಲಿ ಬರೆದುಕೊಡುವಿರಾ?"),
]
ALERT_TITLE = t("You have the right to say no.", "आपको ‘ना’ कहने का हक़ है।", "‘ಇಲ್ಲ’ ಎಂದು ಹೇಳುವ ಹಕ್ಕು ನಿಮಗಿದೆ.")
ALERT_TEXT = t("No one can force you to have surgery. You can take time and see another doctor.",
               "कोई आपको ऑपरेशन के लिए मजबूर नहीं कर सकता। आप समय लेकर दूसरे डॉक्टर से मिल सकती हैं।",
               "ಯಾರೂ ನಿಮ್ಮನ್ನು ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಗೆ ಒತ್ತಾಯಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ. ನೀವು ಸಮಯ ತೆಗೆದುಕೊಂಡು ಇನ್ನೊಬ್ಬ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಬಹುದು.")
# VERIFY these numbers before launch.
HELPLINES = [{"name": "Women Helpline", "number": "181"}, {"name": "Free legal aid (NALSA)", "number": "15100"}, {"name": "Emergency", "number": "112"}]

# Spoken helpline text (voice only). Native-speaker review needed like everything else here.
CALL = t("Call", "कॉल करें", "ಕರೆ ಮಾಡಿ")
HELPLINE_NAMES = {"181": t("Women Helpline", "महिला हेल्पलाइन", "ಮಹಿಳಾ ಸಹಾಯವಾಣಿ"),
                  "15100": t("Free legal aid", "मुफ़्त कानूनी सहायता", "ಉಚಿತ ಕಾನೂನು ನೆರವು"),
                  "112": t("Emergency", "आपातकाल", "ತುರ್ತು ಸೇವೆ")}

# PDF slip labels. Hindi/Kannada need native-speaker review like everything else here.
SLIP_TITLE = t("Zaroori?  Second Opinion Slip", "ज़रूरी?  दूसरी राय की पर्ची", "ಜರೂರಿ?  ಎರಡನೇ ಅಭಿಪ್ರಾಯದ ಚೀಟಿ")
SLIP_META = t("Code: {code}   Date: {date}   District: {district}", "कोड: {code}   तारीख: {date}   ज़िला: {district}", "ಕೋಡ್: {code}   ದಿನಾಂಕ: {date}   ಜಿಲ್ಲೆ: {district}")
SLIP_Q_HEAD = t("Questions to ask the doctor", "डॉक्टर से पूछने के सवाल", "ವೈದ್ಯರನ್ನು ಕೇಳಬೇಕಾದ ಪ್ರಶ್ನೆಗಳು")
SLIP_H_HEAD = t("Government hospitals in your district", "आपके ज़िले के सरकारी अस्पताल", "ನಿಮ್ಮ ಜಿಲ್ಲೆಯ ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಗಳು")
SLIP_NO_HOSP = t("Ask your ASHA didi for the nearest government hospital", "सबसे नज़दीकी सरकारी अस्पताल के लिए अपनी आशा दीदी से पूछिए", "ಹತ್ತಿರದ ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಯ ಬಗ್ಗೆ ನಿಮ್ಮ ಆಶಾ ದೀದಿಯನ್ನು ಕೇಳಿ")
SLIP_FOOT = t("This slip has no name. It is not a diagnosis. It is a reminder to ask once more before a big decision.",
              "इस पर्ची पर कोई नाम नहीं है। यह कोई जांच नहीं है। यह बड़े फ़ैसले से पहले एक बार और पूछने की याद है।",
              "ಈ ಚೀಟಿಯಲ್ಲಿ ಹೆಸರು ಇಲ್ಲ. ಇದು ರೋಗನಿರ್ಣಯ ಅಲ್ಲ. ದೊಡ್ಡ ನಿರ್ಧಾರದ ಮೊದಲು ಇನ್ನೊಮ್ಮೆ ಕೇಳುವ ನೆನಪು.")

# Safety guardrail: no output may ever tell her to refuse surgery or diagnose.
BLOCKLIST = ["don't do surgery", "do not do surgery", "you don't need surgery", "you do not need surgery", "you have fibroids", "you are sick"]
def pick(d, lang): return d.get(lang) or d["en"]
