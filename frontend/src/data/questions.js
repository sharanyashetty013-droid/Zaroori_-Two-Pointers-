const t = (en, hi, kn) => ({ en, hi, kn })

const YES = { value: 'yes', label: t('Yes', 'हाँ', 'ಹೌದು') }
const NO = { value: 'no', label: t('No', 'नहीं', 'ಇಲ್ಲ') }
const DONT_KNOW = { value: 'unknown', label: t("Don't know", 'पता नहीं', 'ಗೊತ್ತಿಲ್ಲ') }

export const UI = {
  listen: t('Listen again', 'फिर से सुनें', 'ಮತ್ತೆ ಕೇಳಿ'),
  back: t('Back', 'पीछे', 'ಹಿಂದೆ'),
}

export const QUESTIONS = [
  {
    id: 'age',
    text: t('How old are you?', 'आपकी उम्र कितनी है?', 'ನಿಮ್ಮ ವಯಸ್ಸು ಎಷ್ಟು?'),
    options: [
      { value: 'under25', label: t('Under 25', '25 से कम', '25ಕ್ಕಿಂತ ಕಡಿಮೆ') },
      { value: '25to30', label: t('25 to 30', '25 से 30', '25 ರಿಂದ 30') },
      { value: '31to35', label: t('31 to 35', '31 से 35', '31 ರಿಂದ 35') },
      { value: 'over35', label: t('Over 35', '35 से ज़्यादा', '35ಕ್ಕಿಂತ ಹೆಚ್ಚು') },
    ],
  },
  {
    id: 'doctorSaid',
    text: t('What did the doctor say?', 'डॉक्टर ने क्या कहा?', 'ವೈದ್ಯರು ಏನು ಹೇಳಿದರು?'),
    options: [
      { value: 'surgery', label: t('Womb must be removed', 'बच्चेदानी निकालनी है', 'ಗರ್ಭಕೋಶ ತೆಗೆಯಬೇಕು') },
      { value: 'medicine', label: t('Medicine or other treatment', 'दवा या दूसरा इलाज', 'ಔಷಧಿ ಅಥವಾ ಬೇರೆ ಚಿಕಿತ್ಸೆ') },
      { value: 'noexplain', label: t('Doctor did not explain', 'डॉक्टर ने समझाया नहीं', 'ವೈದ್ಯರು ವಿವರಿಸಲಿಲ್ಲ') },
    ],
  },
  {
    id: 'tests',
    text: t('Was any test or scan done?', 'क्या कोई जाँच या स्कैन हुआ?', 'ಯಾವುದಾದರೂ ಪರೀಕ್ಷೆ ಅಥವಾ ಸ್ಕ್ಯಾನ್ ಮಾಡಲಾಗಿದೆಯೇ?'),
    options: [YES, NO, DONT_KNOW],
  },
  {
    id: 'secondOpinion',
    text: t('Did you see another doctor?', 'क्या आपने दूसरे डॉक्टर को दिखाया?', 'ನೀವು ಬೇರೆ ವೈದ್ಯರನ್ನು ಕಾಣಿಸಿದ್ದೀರಾ?'),
    options: [YES, NO],
  },
  {
    id: 'children',
    text: t('Do you have children?', 'क्या आपके बच्चे हैं?', 'ನಿಮಗೆ ಮಕ್ಕಳಿದ್ದಾರೆಯೇ?'),
    options: [YES, NO],
  },
  {
    id: 'pressure',
    text: t('Is anyone pressuring you?', 'क्या कोई आप पर दबाव डाल रहा है?', 'ಯಾರಾದರೂ ನಿಮ್ಮ ಮೇಲೆ ಒತ್ತಡ ಹಾಕುತ್ತಿದ್ದಾರೆಯೇ?'),
    options: [YES, NO, { value: 'skip', label: t('Prefer not to say', 'बताना नहीं चाहती', 'ಹೇಳಲು ಇಷ್ಟವಿಲ್ಲ') }],
  },
]
