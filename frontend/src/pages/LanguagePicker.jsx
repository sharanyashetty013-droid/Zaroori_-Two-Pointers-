import { useNavigate } from "react-router-dom";

export default function LanguagePicker({ setLang }) {
  const navigate = useNavigate();

  function choose(code) {
    setLang(code);
    navigate("/questions");
  }

  return (
    <div className="app" style={{ textAlign: "center" }}>
      <h1>Zaroori?</h1>
      <p className="subtitle">Is it necessary? Ask once more before a big decision.</p>

      <div className="card">
        <p style={{ margin: 0, fontWeight: 600 }}>
          Choose a language · भाषा चुनें · ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ
        </p>

        <button className="btn" onClick={() => choose("hi")}>हिंदी</button>
        <button className="btn" onClick={() => choose("kn")}>ಕನ್ನಡ</button>
        <button className="btn" onClick={() => choose("en")}>English</button>
      </div>
    </div>
  );
}