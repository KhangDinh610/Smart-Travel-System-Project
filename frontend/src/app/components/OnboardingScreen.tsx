import { useState } from "react";
import {
  Compass, UtensilsCrossed, Shirt, Gem, Cookie, Palette, Bookmark,
  Coffee, Flower2, Music, Gift, Camera, ShoppingBag, ArrowRight, Check, LogOut
} from "lucide-react";
import { LangToggle } from "./LangToggle";
import { type Lang, type Translations } from "../translations";

interface OnboardingScreenProps {
  tr: Translations["onboarding"];
  lang: Lang;
  setLang: (l: Lang) => void;
  onComplete: () => void;
  onLogout: () => void;
}

const TAG_META = [
  { id: "food", icon: UtensilsCrossed, tag: "#LocalFood", color: "#E2714A", bg: "#FEF0EA" },
  { id: "handicrafts", icon: Gem, tag: "#Handicrafts", color: "#2A9D8F", bg: "#E6F6F4" },
  { id: "clothing", icon: Shirt, tag: "#TraditionalClothing", color: "#8B5CF6", bg: "#F0EEFF" },
  { id: "snacks", icon: Cookie, tag: "#Snacks", color: "#F4A261", bg: "#FEF5EA" },
  { id: "art", icon: Palette, tag: "#ArtPieces", color: "#E76F51", bg: "#FEF0EA" },
  { id: "magnets", icon: Bookmark, tag: "#Magnets", color: "#3B82F6", bg: "#EFF6FF" },
  { id: "tea", icon: Coffee, tag: "#LocalTea", color: "#059669", bg: "#ECFDF5" },
  { id: "flowers", icon: Flower2, tag: "#Florals", color: "#EC4899", bg: "#FDF2F8" },
  { id: "music", icon: Music, tag: "#Instruments", color: "#7C3AED", bg: "#F5F3FF" },
  { id: "gifts", icon: Gift, tag: "#GiftSets", color: "#DC2626", bg: "#FEF2F2" },
  { id: "photo", icon: Camera, tag: "#Photography", color: "#0284C7", bg: "#F0F9FF" },
  { id: "bags", icon: ShoppingBag, tag: "#LocalBags", color: "#B45309", bg: "#FFFBEB" },
] as const;

export function OnboardingScreen({ tr, lang, setLang, onComplete, onLogout }: OnboardingScreenProps) {
  const [selected, setSelected] = useState<Set<string>>(new Set());

  const toggle = (id: string) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const handleNext = () => {
    onComplete();
  };

  return (
    <div className="min-h-screen w-full flex" style={{ background: "#FDF3EB" }}>

      {/* ── Left sidebar (desktop) ── */}
      <aside
        className="hidden lg:flex flex-col flex-shrink-0 w-72 xl:w-80"
        style={{ background: "linear-gradient(160deg, #3D2314 0%, #6B3A2A 100%)", position: "sticky", top: 0, height: "100vh" }}
      >
        <div className="px-8 pt-8 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "rgba(255,255,255,0.15)" }}>
              <Compass size={18} color="white" />
            </div>
            <span style={{ color: "white", fontSize: "18px", fontWeight: 800 }}>SouvenirAI</span>
          </div>
          <LangToggle lang={lang} setLang={setLang} />
        </div>

        <div className="px-8 mt-10">
          <h2 style={{ color: "white", fontSize: "24px", fontWeight: 800, lineHeight: 1.2 }}>{tr.personalizeTitle}</h2>
          <p className="mt-3" style={{ color: "rgba(255,255,255,0.6)", fontSize: "14px", lineHeight: 1.7 }}>{tr.personalizeSubtitle}</p>
        </div>

        {/* Step indicators */}
        <div className="flex flex-col gap-4 px-8 mt-10">
          {[
            { n: 1, label: tr.stepInterests, desc: tr.stepInterestsDesc },
          ].map(({ n, label, desc }) => {
            const active = true;
            return (
              <div key={n} className="flex items-start gap-3">
                <div
                  className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5"
                  style={{
                    background: "rgba(255,255,255,0.2)",
                    border: "2px solid rgba(255,255,255,0.5)",
                  }}
                >
                  <span style={{ color: "white", fontSize: "13px", fontWeight: 700 }}>{n}</span>
                </div>
                <div>
                  <p style={{ color: "white", fontSize: "14px", fontWeight: 700 }}>{label}</p>
                  <p style={{ color: "rgba(255,255,255,0.35)", fontSize: "12px" }}>{desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        <div className="mt-auto px-8 pb-8 flex flex-col gap-2">
          <button
            onClick={onLogout}
            className="flex items-center gap-2 px-4 py-2 rounded-xl transition-all hover:bg-white/10"
            style={{ color: "rgba(255,255,255,0.6)", fontSize: "14px", border: "1px solid rgba(255,255,255,0.15)" }}
          >
            <LogOut size={16} /> {lang === "vi" ? "Đăng xuất" : "Sign out"}
          </button>
          <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "12px" }}>{tr.updateAnytime}</p>
        </div>
      </aside>

      {/* ── Main content ── */}
      <div className="flex-1 flex flex-col">
        {/* Mobile header */}
        <div className="lg:hidden px-6 pt-8 pb-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Compass size={20} style={{ color: "#E2714A" }} />
              <span style={{ color: "#3D2314", fontWeight: 800, fontSize: "17px" }}>SouvenirAI</span>
            </div>
            <div className="flex items-center gap-3">
              <button onClick={onLogout} style={{ color: "#7A4528" }}>
                <LogOut size={20} />
              </button>
              <LangToggle lang={lang} setLang={setLang} />
            </div>
          </div>
          <div className="flex gap-2">
            {[1].map((s) => (
              <div key={s} className="h-1.5 flex-1 rounded-full" style={{ background: "#E2714A" }} />
            ))}
          </div>
          <p className="mt-2" style={{ color: "#B07050", fontSize: "12px" }}>
            {lang === "vi" ? "Bước 1 / 1" : "Step 1 of 1"}
          </p>
        </div>

        <div className="flex-1 px-6 lg:px-12 xl:px-16 py-8 lg:py-12 overflow-y-auto">
          <div className="max-w-3xl">
            <h1 style={{ color: "#3D2314", fontSize: "30px", fontWeight: 900, lineHeight: 1.15 }}>{tr.question1}</h1>
            <p className="mt-2" style={{ color: "#7A4528", fontSize: "15px" }}>{tr.question1sub}</p>
          </div>

          <div className="mt-8 grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 max-w-3xl">
            {TAG_META.map((meta) => {
              const Icon = meta.icon;
              const label = tr.tags[meta.id as keyof typeof tr.tags];
              const isSelected = selected.has(meta.id);
              return (
                <button
                  key={meta.id}
                  onClick={() => toggle(meta.id)}
                  className="flex items-center gap-3 p-4 rounded-2xl text-left transition-all hover:scale-[1.02] active:scale-98"
                  style={{
                    background: isSelected ? meta.bg : "white",
                    border: `2px solid ${isSelected ? meta.color : "#F5CBA7"}`,
                    boxShadow: isSelected ? `0 4px 16px ${meta.color}25` : "0 1px 6px rgba(0,0,0,0.04)",
                  }}
                >
                  <div
                    className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{ background: isSelected ? meta.color : meta.bg }}
                  >
                    <Icon size={18} color={isSelected ? "white" : meta.color} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p style={{ color: isSelected ? meta.color : "#3D2314", fontSize: "13px", fontWeight: 700, lineHeight: 1.3 }}>{label}</p>
                    <p style={{ color: isSelected ? meta.color : "#B07050", fontSize: "11px", opacity: 0.75 }}>{meta.tag}</p>
                  </div>
                  {isSelected && (
                    <div className="flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center" style={{ background: meta.color }}>
                      <Check size={11} color="white" />
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {selected.size > 0 && (
            <p className="mt-4" style={{ color: "#7A4528", fontSize: "14px" }}>{tr.selected(selected.size)}</p>
          )}

          {/* CTA */}
          <div className="mt-10 flex items-center gap-4">
            <button
              onClick={handleNext}
              disabled={selected.size === 0}
              className="flex items-center gap-2 px-8 py-4 rounded-2xl transition-all hover:opacity-90 active:scale-98 disabled:opacity-40 disabled:cursor-not-allowed"
              style={{
                background: "linear-gradient(135deg, #E2714A 0%, #C8562E 100%)",
                color: "white",
                fontWeight: 700,
                fontSize: "15px",
                boxShadow: selected.size > 0 ? "0 6px 24px rgba(226,113,74,0.4)" : "none",
              }}
            >
              {tr.getStarted} <ArrowRight size={16} />
            </button>
            {selected.size === 0 && (
              <p style={{ color: "#B07050", fontSize: "13px" }}>{tr.pickAtLeastOne}</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
