import { useLanguage } from './LanguageContext'

export const STRINGS = {
  en: {
    asha: 'ASHA',
    ashaCode: 'ASHA code',
    district: 'District',
    language: 'Language',
    forAsha: 'For the ASHA',
    exit: 'Exit',
    logout: 'Log out',
    stepLanguage: 'Language',
    stepHospital: 'Hospital',
    stepQuestions: 'Questions',
    stepResult: 'Result',
    stepHelp: 'Help and rights',
    chooseLanguage: 'Choose a language',
    chooseLanguageSub: 'भाषा चुनें · ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ',
    guideStart:
      'Ask in private. Read each question as written. Do not hint at the answer. The woman decides. Never write her name anywhere.',
    hospitalTitle: 'Which hospital advised surgery?',
    hospitalNote: 'This is optional. It is not a report against anyone.',
    guideHospital:
      'Do not say whether surgery is right or wrong. Just ask. If she is not sure, tap "Not sure / skip".',
    skip: 'Not sure / skip',
    loading: 'Loading…',
    noConn: 'No connection',
    retry: 'Try again',
    question: 'Question',
    guideQ_age:
      'You are asking only to give the right information. Her name is not written anywhere.',
    guideQ_doctorSaid:
      'Do not say whether surgery is right or wrong. Just ask, then tap the closest answer.',
    guideQ_tests:
      'Read the question as written. Do not hint at the answer. It is fine if she does not know.',
    guideQ_secondOpinion:
      'A second opinion is normal and her right. Either answer is fine.',
    guideQ_children:
      'Read the question as written. Either answer is fine. Do not comment on it.',
    guideQ_pressure:
      'Ask only when she is alone. Nothing is shared unless she says yes.',
  },
  hi: {
    asha: 'आशा',
    ashaCode: 'आशा कोड',
    district: 'जिला',
    language: 'भाषा',
    forAsha: 'आशा के लिए',
    exit: 'बाहर निकलें',
    logout: 'लॉग आउट',
    stepLanguage: 'भाषा',
    stepHospital: 'अस्पताल',
    stepQuestions: 'प्रश्न',
    stepResult: 'नतीजा',
    stepHelp: 'मदद और अधिकार',
    chooseLanguage: 'भाषा चुनें',
    chooseLanguageSub: 'Choose a language · ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ',
    guideStart:
      'अकेले में पूछें। हर सवाल जैसा लिखा है वैसा ही पढ़ें। जवाब का इशारा न दें। फ़ैसला महिला का है। उसका नाम कहीं न लिखें।',
    hospitalTitle: 'किस अस्पताल ने ऑपरेशन की सलाह दी?',
    hospitalNote: 'यह वैकल्पिक है। यह किसी के ख़िलाफ़ शिकायत नहीं है।',
    guideHospital:
      'यह न कहें कि ऑपरेशन सही है या गलत। बस पूछें। अगर उसे पता नहीं है, तो "पता नहीं / छोड़ें" दबाएँ।',
    skip: 'पता नहीं / छोड़ें',
    loading: 'लोड हो रहा है…',
    noConn: 'कनेक्शन नहीं है',
    retry: 'फिर कोशिश करें',
    question: 'प्रश्न',
    guideQ_age:
      'आप सिर्फ़ सही जानकारी देने के लिए पूछ रही हैं। उसका नाम कहीं नहीं लिखा जाता।',
    guideQ_doctorSaid:
      'यह न कहें कि ऑपरेशन सही है या गलत। बस पूछें, फिर सबसे नज़दीकी जवाब दबाएँ।',
    guideQ_tests:
      'सवाल जैसा लिखा है वैसा पढ़ें। जवाब का इशारा न दें। अगर उसे पता नहीं है तो यह ठीक है।',
    guideQ_secondOpinion:
      'दूसरे डॉक्टर की राय लेना आम बात है और उसका हक़ है। कोई भी जवाब ठीक है।',
    guideQ_children:
      'सवाल जैसा लिखा है वैसा पढ़ें। कोई भी जवाब ठीक है। उस पर कुछ न कहें।',
    guideQ_pressure:
      'यह तभी पूछें जब वह अकेली हो। वह हाँ कहे तभी कुछ साझा होगा।',
  },
  kn: {
    asha: 'ಆಶಾ',
    ashaCode: 'ಆಶಾ ಕೋಡ್',
    district: 'ಜಿಲ್ಲೆ',
    language: 'ಭಾಷೆ',
    forAsha: 'ಆಶಾ ಅವರಿಗೆ',
    exit: 'ನಿರ್ಗಮಿಸಿ',
    logout: 'ಲಾಗ್ ಔಟ್',
    stepLanguage: 'ಭಾಷೆ',
    stepHospital: 'ಆಸ್ಪತ್ರೆ',
    stepQuestions: 'ಪ್ರಶ್ನೆಗಳು',
    stepResult: 'ಫಲಿತಾಂಶ',
    stepHelp: 'ಸಹಾಯ ಮತ್ತು ಹಕ್ಕುಗಳು',
    chooseLanguage: 'ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ',
    chooseLanguageSub: 'Choose a language · भाषा चुनें',
    guideStart:
      'ಏಕಾಂತದಲ್ಲಿ ಕೇಳಿ. ಪ್ರತಿ ಪ್ರಶ್ನೆಯನ್ನು ಬರೆದಂತೆಯೇ ಓದಿ. ಉತ್ತರದ ಸುಳಿವು ನೀಡಬೇಡಿ. ನಿರ್ಧಾರ ಮಹಿಳೆಯದು. ಅವರ ಹೆಸರನ್ನು ಎಲ್ಲಿಯೂ ಬರೆಯಬೇಡಿ.',
    hospitalTitle: 'ಯಾವ ಆಸ್ಪತ್ರೆ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆಯ ಸಲಹೆ ನೀಡಿತು?',
    hospitalNote: 'ಇದು ಐಚ್ಛಿಕ. ಇದು ಯಾರ ವಿರುದ್ಧವೂ ದೂರು ಅಲ್ಲ.',
    guideHospital:
      'ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ ಸರಿಯೋ ತಪ್ಪೋ ಎಂದು ಹೇಳಬೇಡಿ. ಕೇವಲ ಕೇಳಿ. ಅವರಿಗೆ ಗೊತ್ತಿಲ್ಲದಿದ್ದರೆ "ಗೊತ್ತಿಲ್ಲ / ಬಿಟ್ಟುಬಿಡಿ" ಒತ್ತಿ.',
    skip: 'ಗೊತ್ತಿಲ್ಲ / ಬಿಟ್ಟುಬಿಡಿ',
    loading: 'ಲೋಡ್ ಆಗುತ್ತಿದೆ…',
    noConn: 'ಸಂಪರ್ಕ ಇಲ್ಲ',
    retry: 'ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ',
    question: 'ಪ್ರಶ್ನೆ',
    guideQ_age:
      'ಸರಿಯಾದ ಮಾಹಿತಿ ನೀಡಲು ಮಾತ್ರ ನೀವು ಕೇಳುತ್ತಿದ್ದೀರಿ. ಅವರ ಹೆಸರನ್ನು ಎಲ್ಲಿಯೂ ಬರೆಯುವುದಿಲ್ಲ.',
    guideQ_doctorSaid:
      'ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ ಸರಿಯೋ ತಪ್ಪೋ ಎಂದು ಹೇಳಬೇಡಿ. ಕೇವಲ ಕೇಳಿ, ನಂತರ ಹತ್ತಿರದ ಉತ್ತರವನ್ನು ಒತ್ತಿ.',
    guideQ_tests:
      'ಪ್ರಶ್ನೆಯನ್ನು ಬರೆದಂತೆಯೇ ಓದಿ. ಉತ್ತರದ ಸುಳಿವು ನೀಡಬೇಡಿ. ಅವರಿಗೆ ಗೊತ್ತಿಲ್ಲದಿದ್ದರೂ ಪರವಾಗಿಲ್ಲ.',
    guideQ_secondOpinion:
      'ಎರಡನೇ ವೈದ್ಯರ ಅಭಿಪ್ರಾಯ ಪಡೆಯುವುದು ಸಾಮಾನ್ಯ ಮತ್ತು ಅವರ ಹಕ್ಕು. ಯಾವ ಉತ್ತರವೂ ಸರಿ.',
    guideQ_children:
      'ಪ್ರಶ್ನೆಯನ್ನು ಬರೆದಂತೆಯೇ ಓದಿ. ಯಾವ ಉತ್ತರವೂ ಸರಿ. ಅದರ ಬಗ್ಗೆ ಏನೂ ಹೇಳಬೇಡಿ.',
    guideQ_pressure:
      'ಅವರು ಒಂಟಿಯಾಗಿರುವಾಗ ಮಾತ್ರ ಕೇಳಿ. ಅವರು ಹೌದು ಎಂದರೆ ಮಾತ್ರ ಏನನ್ನಾದರೂ ಹಂಚಲಾಗುತ್ತದೆ.',
  },
}

export function useT() {
  const { lang } = useLanguage()
  return (key) => STRINGS[lang]?.[key] ?? STRINGS.en[key] ?? key
}