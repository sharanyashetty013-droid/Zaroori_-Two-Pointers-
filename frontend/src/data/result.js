const t = (en, hi, kn) => ({ en, hi, kn })

export const RESULT = {
  headline: t('Get a second opinion first', 'पहले दूसरी राय लें', 'ಮೊದಲು ಎರಡನೇ ಅಭಿಪ್ರಾಯ ಪಡೆಯಿರಿ'),
  body: t(
    'This is a big decision. Before you decide, ask once more.',
    'यह एक बड़ा फ़ैसला है। फ़ैसला करने से पहले एक बार और पूछें।',
    'ಇದು ದೊಡ್ಡ ನಿರ್ಧಾರ. ನಿರ್ಧರಿಸುವ ಮೊದಲು ಇನ್ನೊಮ್ಮೆ ಕೇಳಿ.'
  ),
  askTitle: t('Ask the doctor', 'डॉक्टर से पूछें', 'ವೈದ್ಯರನ್ನು ಕೇಳಿ'),
  ask: [
    t('Why do I need this treatment?', 'मुझे यह इलाज क्यों ज़रूरी है?', 'ನನಗೆ ಈ ಚಿಕಿತ್ಸೆ ಏಕೆ ಬೇಕು?'),
    t('Is there any other treatment, like medicine?', 'क्या दवा जैसा कोई दूसरा इलाज है?', 'ಔಷಧಿಯಂತಹ ಬೇರೆ ಚಿಕಿತ್ಸೆ ಇದೆಯೇ?'),
    t('Which test or scan shows this problem?', 'कौन सी जाँच या स्कैन में यह समस्या दिखी?', 'ಯಾವ ಪರೀಕ್ಷೆ ಅಥವಾ ಸ್ಕ್ಯಾನ್‌ನಲ್ಲಿ ಈ ಸಮಸ್ಯೆ ಕಂಡಿದೆ?'),
    t('What happens if I wait?', 'अगर मैं इंतज़ार करूँ तो क्या होगा?', 'ನಾನು ಕಾಯ್ದರೆ ಏನಾಗುತ್ತದೆ?'),
    t('Can I show my reports to another doctor?', 'क्या मैं अपनी रिपोर्ट दूसरे डॉक्टर को दिखा सकती हूँ?', 'ನನ್ನ ವರದಿಗಳನ್ನು ಬೇರೆ ವೈದ್ಯರಿಗೆ ತೋರಿಸಬಹುದೇ?'),
  ],
  visitTitle: t('Visit a government hospital', 'सरकारी अस्पताल जाएँ', 'ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆಗೆ ಹೋಗಿ'),
  // TODO: replace with a real hospital per district
  visitName: t('Nearest District Government Hospital', 'नज़दीकी ज़िला सरकारी अस्पताल', 'ಹತ್ತಿರದ ಜಿಲ್ಲಾ ಸರ್ಕಾರಿ ಆಸ್ಪತ್ರೆ'),
  hospitalLabel: t('Which hospital advised this?', 'यह सलाह किस अस्पताल ने दी?', 'ಈ ಸಲಹೆಯನ್ನು ಯಾವ ಆಸ್ಪತ್ರೆ ನೀಡಿತು?'),
  hospitalPick: t('Choose hospital', 'अस्पताल चुनें', 'ಆಸ್ಪತ್ರೆ ಆಯ್ಕೆಮಾಡಿ'),
  listen: t('Listen', 'सुनें', 'ಕೇಳಿ'),
  startOver: t('Start over', 'फिर से शुरू करें', 'ಮತ್ತೆ ಪ್ರಾರಂಭಿಸಿ'),
}

// TODO: replace these sample names with real ones (ask your teammate)
export const HOSPITALS = [
  { id: 'h1', name: 'Hospital A (sample)' },
  { id: 'h2', name: 'Hospital B (sample)' },
  { id: 'h3', name: 'Hospital C (sample)' },
  { id: 'other', name: 'Other / not sure' },
]