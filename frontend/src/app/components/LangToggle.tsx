import { type Lang } from "../translations";

interface LangToggleProps {
  lang: Lang;
  setLang: (l: Lang) => void;
}

export function LangToggle({ lang, setLang }: LangToggleProps) {
  return (
    <div className="flex rounded-xl overflow-hidden" style={{ border: "1.5px solid rgba(226,113,74,0.3)", background: "rgba(253,243,235,0.8)" }}>
      {(["en", "vi"] as Lang[]).map((l) => (
        <button
          key={l}
          onClick={() => setLang(l)}
          className="px-3 py-1.5 transition-all"
          style={{
            background: lang === l ? "#E2714A" : "transparent",
            color: lang === l ? "white" : "#7A4528",
            fontSize: "12px",
            fontWeight: 700,
            letterSpacing: "0.3px",
          }}
        >
          {l === "en" ? "EN" : "VI"}
        </button>
      ))}
    </div>
  );
}

export function LangToggleLight({ lang, setLang }: LangToggleProps) {
  return (
    <div className="flex rounded-xl overflow-hidden" style={{ border: "1.5px solid rgba(255,255,255,0.25)" }}>
      {(["en", "vi"] as Lang[]).map((l) => (
        <button
          key={l}
          onClick={() => setLang(l)}
          className="px-3 py-1.5 transition-all"
          style={{
            background: lang === l ? "rgba(255,255,255,0.25)" : "transparent",
            color: "white",
            fontSize: "12px",
            fontWeight: lang === l ? 700 : 500,
            opacity: lang === l ? 1 : 0.6,
          }}
        >
          {l === "en" ? "EN" : "VI"}
        </button>
      ))}
    </div>
  );
}
