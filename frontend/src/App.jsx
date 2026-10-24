import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import LanguagePicker from "./pages/LanguagePicker";
import Questions from "./pages/Questions";
import Result from "./pages/Result";
import Alert from "./pages/Alert";
import Dashboard from "./pages/Dashboard";

export default function App() {
  const [lang, setLang] = useState("en");

  return (
    <Routes>
      <Route path="/" element={<LanguagePicker setLang={setLang} />} />
      <Route path="/questions" element={<Questions lang={lang} />} />
      <Route path="/result" element={<Result lang={lang} />} />
      <Route path="/alert" element={<Alert lang={lang} />} />
      <Route path="/dashboard" element={<Dashboard />} />
    </Routes>
  );
}