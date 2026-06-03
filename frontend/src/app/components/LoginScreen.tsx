import { useState } from "react";
import { Eye, EyeOff, MapPin, Compass, AlertCircle } from "lucide-react";
import { ImageWithFallback } from "./figma/ImageWithFallback";
import { LangToggle, LangToggleLight } from "./LangToggle";
import { type Lang, type Translations } from "../translations";
import { api, type User } from "../../api";
import { auth, googleProvider } from "../firebase";
import { signInWithPopup } from "firebase/auth";

interface LoginScreenProps {
  tr: Translations["login"];
  lang: Lang;
  setLang: (l: Lang) => void;
  onLogin: (user: User) => void;
}

const INPUT_BASE: React.CSSProperties = {
  background: "white",
  border: "1.5px solid #F5CBA7",
  color: "#3D2314",
  fontSize: "15px",
  outline: "none",
  width: "100%",
  borderRadius: "12px",
  padding: "12px 16px",
  transition: "border-color 0.15s",
};

function Field({
  label,
  type,
  value,
  onChange,
  placeholder,
  error,
  rightSlot,
}: {
  label: string;
  type: string;
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  error?: string;
  rightSlot?: React.ReactNode;
}) {
  return (
    <div>
      <label style={{ color: "#3D2314", fontSize: "13px", fontWeight: 600, display: "block", marginBottom: "6px" }}>
        {label}
      </label>
      <div className="relative">
        <input
          type={type}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          style={{ ...INPUT_BASE, paddingRight: rightSlot ? "44px" : "16px", borderColor: error ? "#DC2626" : "#F5CBA7" }}
          onFocus={(e) => { if (!error) e.currentTarget.style.borderColor = "#E2714A"; }}
          onBlur={(e) => { if (!error) e.currentTarget.style.borderColor = "#F5CBA7"; }}
        />
        {rightSlot && (
          <div className="absolute right-3 top-1/2 -translate-y-1/2">{rightSlot}</div>
        )}
      </div>
      {error && (
        <p className="flex items-center gap-1 mt-1" style={{ color: "#DC2626", fontSize: "12px" }}>
          <AlertCircle size={12} /> {error}
        </p>
      )}
    </div>
  );
}

export function LoginScreen({ tr, lang, setLang, onLogin }: LoginScreenProps) {
  const [tab, setTab] = useState<"signin" | "signup">("signin");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPass, setShowPass] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const testimonials = [tr.testimonial1, tr.testimonial2, tr.testimonial3];

  const validate = () => {
    const errs: Record<string, string> = {};
    if (tab === "signup" && !name.trim()) errs.name = lang === "vi" ? "Vui lòng nhập họ tên" : "Name is required";
    if (!email.trim()) errs.email = lang === "vi" ? "Vui lòng nhập email" : "Email is required";
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = lang === "vi" ? "Email không hợp lệ" : "Invalid email address";
    if (!password) errs.password = lang === "vi" ? "Vui lòng nhập mật khẩu" : "Password is required";
    else if (password.length < 6) errs.password = lang === "vi" ? "Mật khẩu tối thiểu 6 ký tự" : "At least 6 characters";
    if (tab === "signup" && password !== confirmPassword) errs.confirm = tr.passwordMismatch;
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async () => {
    if (!validate()) return;
    setIsLoading(true);
    setErrors({});
    try {
      if (tab === "signup") {
        await api.register(email, password);
        // Automatically login after register
        const userRes = await api.login(email, password);
        onLogin({ ...userRes, is_new_user: true });
      } else {
        const userRes = await api.login(email, password);
        onLogin(userRes);
      }
    } catch (error: any) {
      setErrors({ form: error.message || "An error occurred" });
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);
    setErrors({});
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const token = await result.user.getIdToken();
      
      // Use a new API method for Firebase token login
      const userRes = await api.loginWithFirebase(token);
      onLogin(userRes);
    } catch (error: any) {
      console.error("Google login error", error);
      setErrors({ form: error.message || "Google login failed" });
    } finally {
      setIsLoading(false);
    }
  };

  const eyeBtn = (show: boolean, toggle: () => void) => (
    <button type="button" onClick={toggle} style={{ color: "#B07050", lineHeight: 0 }}>
      {show ? <EyeOff size={17} /> : <Eye size={17} />}
    </button>
  );

  return (
    <div className="min-h-screen w-full flex">

      {/* ── Left panel — hero (desktop only) ── */}
      <div
        className="hidden lg:flex lg:w-1/2 xl:w-3/5 relative flex-col"
        style={{ background: "linear-gradient(145deg, #3D2314 0%, #6B3A2A 55%, #E2714A 100%)" }}
      >
        <div className="absolute inset-0">
          <ImageWithFallback
            src="https://images.unsplash.com/photo-1764577327260-e4bd407cadda?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx0cmF2ZWwlMjBzb3V2ZW5pciUyMGxvY2FsJTIwbWFya2V0JTIwYXNpYXxlbnwxfHx8fDE3NzkyMDMzNjB8MA&ixlib=rb-4.1.0&q=80&w=1080"
            alt="Market"
            className="w-full h-full object-cover opacity-25"
          />
        </div>

        <div className="relative z-10 flex flex-col h-full p-12">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "rgba(255,255,255,0.2)", backdropFilter: "blur(8px)" }}>
                <Compass size={22} color="white" />
              </div>
              <span style={{ color: "white", fontSize: "22px", fontWeight: 800, letterSpacing: "-0.5px" }}>SouvenirAI</span>
            </div>
            <LangToggleLight lang={lang} setLang={setLang} />
          </div>

          <div className="mt-auto mb-auto flex flex-col gap-6">
            <div>
              <h1 style={{ color: "white", fontSize: "44px", fontWeight: 900, lineHeight: 1.1, letterSpacing: "-1px" }}>
                {tr.tagline}
              </h1>
              <p className="mt-4" style={{ color: "rgba(255,255,255,0.72)", fontSize: "16px", lineHeight: 1.75, maxWidth: "460px" }}>
                {tr.heroSubtitle}
              </p>
            </div>

            <div className="flex flex-col gap-3 mt-2">
              {testimonials.map((t, i) => (
                <div key={i} className="p-4 rounded-2xl" style={{ background: "rgba(255,255,255,0.11)", backdropFilter: "blur(12px)", border: "1px solid rgba(255,255,255,0.14)" }}>
                  <p style={{ color: "rgba(255,255,255,0.88)", fontSize: "13px", lineHeight: 1.65 }}>"{t.text}"</p>
                  <p className="mt-2" style={{ color: "rgba(255,255,255,0.48)", fontSize: "12px", fontWeight: 600 }}>— {t.author} {t.country}</p>
                </div>
              ))}
            </div>
          </div>

          <p style={{ color: "rgba(255,255,255,0.3)", fontSize: "12px" }}>© 2026 SouvenirAI</p>
        </div>
      </div>

      {/* ── Right panel — form ── */}
      <div
        className="w-full lg:w-1/2 xl:w-2/5 flex flex-col justify-center px-6 sm:px-10 lg:px-14 py-10"
        style={{ background: "#FDF3EB", minHeight: "100vh" }}
      >
        {/* Mobile top bar */}
        <div className="flex lg:hidden items-center justify-between mb-8">
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: "#E2714A" }}>
              <Compass size={20} color="white" />
            </div>
            <span style={{ color: "#3D2314", fontSize: "20px", fontWeight: 800 }}>SouvenirAI</span>
          </div>
          <LangToggle lang={lang} setLang={setLang} />
        </div>

        <div className="w-full max-w-sm mx-auto">
          {/* Desktop lang toggle */}
          <div className="hidden lg:flex justify-end mb-6">
            <LangToggle lang={lang} setLang={setLang} />
          </div>

          {/* Tab switcher */}
          <div className="flex rounded-2xl p-1.5 mb-7" style={{ background: "#F5CBA7" }}>
            {([["signin", tr.tabSignIn], ["signup", tr.tabSignUp]] as const).map(([key, label]) => (
              <button
                key={key}
                onClick={() => { setTab(key); setErrors({}); }}
                className="flex-1 py-2.5 rounded-xl transition-all"
                style={{
                  background: tab === key ? "white" : "transparent",
                  color: tab === key ? "#E2714A" : "#7A4528",
                  fontWeight: 700,
                  fontSize: "14px",
                  boxShadow: tab === key ? "0 1px 6px rgba(61,35,20,0.12)" : "none",
                }}
              >
                {label}
              </button>
            ))}
          </div>

          {/* Heading */}
          <div className="mb-6">
            <h2 style={{ color: "#3D2314", fontSize: "26px", fontWeight: 800, lineHeight: 1.2 }}>
              {tab === "signin" ? tr.signInTitle : tr.signUpTitle}
            </h2>
            <p className="mt-1.5" style={{ color: "#7A4528", fontSize: "14px" }}>
              {tab === "signin" ? tr.signInSubtitle : tr.signUpSubtitle}
            </p>
          </div>

          {/* Form fields */}
          <div className="flex flex-col gap-4">
            {tab === "signup" && (
              <Field
                label={tr.fullName}
                type="text"
                value={name}
                onChange={setName}
                placeholder={tr.fullNamePlaceholder}
                error={errors.name}
              />
            )}

            <Field
              label={tr.email}
              type="email"
              value={email}
              onChange={setEmail}
              placeholder={tr.emailPlaceholder}
              error={errors.email}
            />

            <Field
              label={tr.password}
              type={showPass ? "text" : "password"}
              value={password}
              onChange={setPassword}
              placeholder={tr.passwordPlaceholder}
              error={errors.password}
              rightSlot={eyeBtn(showPass, () => setShowPass(!showPass))}
            />

            {tab === "signup" && (
              <Field
                label={tr.confirmPassword}
                type={showConfirm ? "text" : "password"}
                value={confirmPassword}
                onChange={setConfirmPassword}
                placeholder={tr.confirmPasswordPlaceholder}
                error={errors.confirm}
                rightSlot={eyeBtn(showConfirm, () => setShowConfirm(!showConfirm))}
              />
            )}

            {tab === "signin" && (
              <div className="text-right -mt-2">
                <button style={{ color: "#E2714A", fontSize: "13px", fontWeight: 600 }}>{tr.forgotPassword}</button>
              </div>
            )}

            {errors.form && (
              <p className="text-center" style={{ color: "#DC2626", fontSize: "13px", fontWeight: 600 }}>
                {errors.form}
              </p>
            )}

            {/* Primary CTA */}
            <button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full py-3.5 rounded-xl mt-1 transition-all hover:opacity-92 active:scale-[0.98] disabled:opacity-50"
              style={{
                background: "linear-gradient(135deg, #E2714A 0%, #C8562E 100%)",
                color: "white",
                fontWeight: 700,
                fontSize: "15px",
                boxShadow: "0 4px 20px rgba(226,113,74,0.38)",
              }}
            >
              {isLoading ? "..." : (tab === "signin" ? tr.btnSignIn : tr.btnSignUp)} →
            </button>

            {/* Divider */}
            <div className="flex items-center gap-3">
              <div className="flex-1 h-px" style={{ background: "#F5CBA7" }} />
              <span style={{ color: "#B07050", fontSize: "12px", whiteSpace: "nowrap" }}>{tr.orContinueWith}</span>
              <div className="flex-1 h-px" style={{ background: "#F5CBA7" }} />
            </div>

            {/* Google button */}
            <button
              onClick={handleGoogleLogin}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-3 py-3.5 rounded-xl transition-all hover:shadow-lg hover:scale-[1.01] active:scale-[0.98] disabled:opacity-50"
              style={{
                background: "white",
                border: "1.5px solid #F5CBA7",
                boxShadow: "0 2px 12px rgba(61,35,20,0.07)",
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              <span style={{ color: "#3D2314", fontWeight: 700, fontSize: "15px" }}>{tr.continueWithGoogle}</span>
            </button>
          </div>

          {/* Footer notes */}
          <p className="mt-5 text-center" style={{ color: "#B07050", fontSize: "12px", lineHeight: 1.6 }}>
            {tr.privacyNote}
          </p>

          <div className="flex items-center justify-center gap-1.5 mt-4">
            <MapPin size={12} style={{ color: "#B07050" }} />
            <span style={{ color: "#B07050", fontSize: "12px" }}>{tr.locationNote}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
