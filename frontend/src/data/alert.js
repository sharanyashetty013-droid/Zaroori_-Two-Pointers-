const t = (en, hi, kn) => ({ en, hi, kn })

export const ALERT = {
  headline: t('You are not alone', 'आप अकेली नहीं हैं', 'ನೀವು ಒಬ್ಬಂಟಿಯಲ್ಲ'),
  body: t(
    'No one can force you to have surgery. This is your body and your decision.',
    'कोई भी आपको ऑपरेशन के लिए मजबूर नहीं कर सकता। यह आपका शरीर है और आपका फ़ैसला है।',
    'ಯಾರೂ ನಿಮ್ಮನ್ನು ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಗೆ ಒತ್ತಾಯಿಸುವಂತಿಲ್ಲ. ಇದು ನಿಮ್ಮ ದೇಹ, ನಿಮ್ಮ ನಿರ್ಧಾರ.'
  ),
  rightsTitle: t('Your rights', 'आपके अधिकार', 'ನಿಮ್ಮ ಹಕ್ಕುಗಳು'),
  rights: [
    t('You can say no.', 'आप मना कर सकती हैं।', 'ನೀವು ಬೇಡ ಎನ್ನಬಹುದು.'),
    t('You have the right to understand your treatment.', 'आपको अपना इलाज समझने का अधिकार है।', 'ನಿಮ್ಮ ಚಿಕಿತ್ಸೆಯನ್ನು ತಿಳಿದುಕೊಳ್ಳುವ ಹಕ್ಕು ನಿಮಗಿದೆ.'),
    t('You have the right to a second opinion.', 'आपको दूसरी राय लेने का अधिकार है।', 'ಎರಡನೇ ಅಭಿಪ್ರಾಯ ಪಡೆಯುವ ಹಕ್ಕು ನಿಮಗಿದೆ.'),
    t('Nothing can be done to you without your free consent.', 'आपकी अपनी मर्ज़ी के बिना आपके साथ कुछ नहीं किया जा सकता।', 'ನಿಮ್ಮ ಸ್ವಂತ ಒಪ್ಪಿಗೆ ಇಲ್ಲದೆ ನಿಮಗೆ ಏನನ್ನೂ ಮಾಡುವಂತಿಲ್ಲ.'),
  ],
  helpTitle: t('Call for help', 'मदद के लिए फ़ोन करें', 'ಸಹಾಯಕ್ಕಾಗಿ ಕರೆ ಮಾಡಿ'),
  consentTitle: t(
    'Do you want us to tell an NGO or officer today?',
    'क्या आप चाहती हैं कि हम आज किसी NGO या अधिकारी को बताएँ?',
    'ಇಂದೇ ಯಾವುದಾದರೂ ಎನ್‌ಜಿಒ ಅಥವಾ ಅಧಿಕಾರಿಗೆ ತಿಳಿಸಬೇಕೇ?'
  ),
  consentNote: t('Your name is never sent.', 'आपका नाम कभी नहीं भेजा जाएगा।', 'ನಿಮ್ಮ ಹೆಸರನ್ನು ಎಂದಿಗೂ ಕಳುಹಿಸಲಾಗುವುದಿಲ್ಲ.'),
  yes: t('Yes, tell them', 'हाँ, बताइए', 'ಹೌದು, ತಿಳಿಸಿ'),
  no: t('No, not now', 'नहीं, अभी नहीं', 'ಬೇಡ, ಈಗ ಬೇಡ'),
  sent: t(
    'Thank you. Your request has been noted.',
    'धन्यवाद। आपका अनुरोध दर्ज कर लिया गया है।',
    'ಧನ್ಯವಾದ. ನಿಮ್ಮ ವಿನಂತಿಯನ್ನು ದಾಖಲಿಸಲಾಗಿದೆ.'
  ),
  declined: t(
    'Okay. You can still call any number above.',
    'ठीक है। आप ऊपर के किसी भी नंबर पर फ़ोन कर सकती हैं।',
    'ಸರಿ. ನೀವು ಮೇಲಿನ ಯಾವುದೇ ಸಂಖ್ಯೆಗೆ ಕರೆ ಮಾಡಬಹುದು.'
  ),
  plan: t('See second-opinion plan', 'दूसरी राय की योजना देखें', 'ಎರಡನೇ ಅಭಿಪ್ರಾಯದ ಯೋಜನೆ ನೋಡಿ'),
  listen: t('Listen', 'सुनें', 'ಕೇಳಿ'),
}

// TODO: confirm this list with your teammate before the demo
export const HELPLINES = [
  { number: '181', label: t('Women Helpline', 'महिला हेल्पलाइन', 'ಮಹಿಳಾ ಸಹಾಯವಾಣಿ') },
  { number: '112', label: t('Emergency (police)', 'आपातकाल (पुलिस)', 'ತುರ್ತು ಸಹಾಯ (ಪೊಲೀಸ್)') },
  { number: '7827170170', label: t('National Commission for Women', 'राष्ट्रीय महिला आयोग', 'ರಾಷ್ಟ್ರೀಯ ಮಹಿಳಾ ಆಯೋಗ') },
  { number: '15100', label: t('Free legal aid', 'मुफ़्त कानूनी सहायता', 'ಉಚಿತ ಕಾನೂನು ನೆರವು') },
]