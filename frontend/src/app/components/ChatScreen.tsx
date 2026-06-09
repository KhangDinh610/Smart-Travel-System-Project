import { useState, useEffect, useRef } from "react";
import {
  MessageCircle, Plus, Send, Sparkles, X, ChevronLeft,
  Calendar, MapPin, Search, Menu, Home, Bookmark, User, LogOut, ArrowLeft
} from "lucide-react";
import { api, type ChatSession, type ChatMessage, type User as ApiUser } from "../../api";
import { type Lang, type Translations } from "../translations";
import { LangToggle } from "./LangToggle";

interface ChatScreenProps {
  tr: Translations["home"]; // Reusing home translations for sidebar
  lang: Lang;
  setLang: (l: Lang) => void;
  user: ApiUser | null;
  onNavigate: (s: any) => void;
  onLogout: () => void;
  initialSessionId?: number;
  initialMessage?: string;
}

export function ChatScreen({ tr, lang, setLang, user, onNavigate, initialSessionId, initialMessage }: ChatScreenProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeSession, setActiveSession] = useState<number | null>(initialSessionId || null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSessions();
  }, [user]);

  useEffect(() => {
    if (activeSession) {
      fetchMessages(activeSession);
    } else {
      setMessages([]);
    }
  }, [activeSession]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Handle initial message if provided
  useEffect(() => {
    if (initialMessage && activeSession) {
       // Check if this was just created and we need to send the first message
       // For now, let's keep it simple
    }
  }, [initialMessage, activeSession]);

  const fetchSessions = async () => {
    if (!user) return;
    try {
      const data = await api.getChatSessions();
      setSessions(data);
      if (data.length > 0 && !activeSession) {
        setActiveSession(data[0].id);
      }
    } catch (e) {
      console.error("Failed to fetch sessions", e);
    }
  };

  const fetchMessages = async (sessionId: number) => {
    try {
      const data = await api.getChatMessages(sessionId);
      setMessages(data);
    } catch (e) {
      console.error("Failed to fetch messages", e);
    }
  };

  const startNewSession = async () => {
    if (!user) return;
    try {
      const title = lang === "vi" ? `Phiên chat mới ${new Date().toLocaleDateString("vi-VN")}` : `New Trip Chat ${new Date().toLocaleDateString()}`;
      const newSession = await api.createChatSession(title);
      setSessions([newSession, ...sessions]);
      setActiveSession(newSession.id);
    } catch (e) {
      console.error("Failed to create session", e);
    }
  };

  const sendMessage = async () => {
    if (!input.trim() || !activeSession || isLoading) return;
    
    const text = input;
    setInput("");
    setIsLoading(true);

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      session_id: activeSession,
      sender: "user",
      text,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempUserMsg]);

    try {
      const aiMsg = await api.sendChatMessage(activeSession, text);
      setMessages(prev => [...prev.filter(m => m.id !== tempUserMsg.id), tempUserMsg, aiMsg]);
    } catch (e) {
      console.error("Failed to send message", e);
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        session_id: activeSession,
        sender: "ai",
        text: "I am sorry, but I encountered an error. Please try again.",
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (text: string) => {
    const lines = text.split("\n");
    const renderInline = (inlineText: string) => {
      const parts = inlineText.split(/(\*\*.*?\*\*|\*.*?\*)/g);
      return parts.map((part, i) => {
        if (part.startsWith("**") && part.endsWith("**")) return <strong key={i}>{part.slice(2, -2)}</strong>;
        if (part.startsWith("*") && part.endsWith("*")) return <em key={i} style={{ fontStyle: "italic" }}>{part.slice(1, -1)}</em>;
        return part;
      });
    };

    return lines.map((line, i) => {
      const trimmedLine = line.trim();
      if (trimmedLine === "---") return <hr key={i} style={{ margin: "12px 0", border: "none", borderTop: "1.5px solid #F5CBA7" }} />;
      if (line.startsWith("###")) return <h3 key={i} style={{ fontWeight: 800, fontSize: "16px", marginTop: "14px", marginBottom: "6px", color: "#E2714A" }}>{renderInline(line.replace(/^###\s*/, ""))}</h3>;
      if (trimmedLine.startsWith("* ") || trimmedLine.startsWith("- ")) {
        return <div key={i} className="flex gap-2 ml-2 mb-1.5"><span style={{ color: "#E2714A", fontWeight: 900 }}>•</span><span style={{ flex: 1 }}>{renderInline(trimmedLine.replace(/^[*|-]\s*/, ""))}</span></div>;
      }
      if (/^\d+\.\s/.test(trimmedLine)) {
        return <div key={i} className="flex gap-2 mb-1.5"><span style={{ fontWeight: 800, color: "#E2714A", minWidth: "18px" }}>{trimmedLine.match(/^\d+\./)?.[0]}</span><span style={{ flex: 1 }}>{renderInline(trimmedLine.replace(/^\d+\.\s*/, ""))}</span></div>;
      }
      if (trimmedLine === "") return <div key={i} style={{ height: "8px" }} />;
      return <p key={i} style={{ marginBottom: "4px", lineHeight: 1.6 }}>{renderInline(line)}</p>;
    });
  };

  return (
    <div className="flex h-screen w-full overflow-hidden" style={{ background: "#FDF3EB" }}>
      
      {/* ── Sidebar ── */}
      <aside
        className={`hidden lg:flex flex-col flex-shrink-0 transition-all duration-300 ${isSidebarOpen ? "w-72 xl:w-80" : "w-0 opacity-0 overflow-hidden"}`}
        style={{ background: "#3D2314", position: "relative" }}
      >
        <div className="px-6 pt-8 pb-5 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: "rgba(255,255,255,0.15)" }}>
              <Sparkles size={18} color="white" />
            </div>
            <span style={{ color: "white", fontSize: "18px", fontWeight: 800 }}>BuyAI Assistant</span>
          </div>
        </div>

        <div className="px-4 mb-4">
          <button
            onClick={startNewSession}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl transition-all hover:bg-white/10"
            style={{ background: "#E2714A", color: "white", fontWeight: 700, fontSize: "14px" }}
          >
            <Plus size={18} /> {lang === "vi" ? "Bắt đầu chuyến đi mới" : "Start New Trip"}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 custom-scrollbar">
          <p className="px-3 mb-2 text-[11px] font-bold uppercase tracking-wider text-white/30">{lang === "vi" ? "LỊCH SỬ CHUYẾN ĐI" : "TRIP HISTORY"}</p>
          <div className="flex flex-col gap-1">
            {sessions.map((s) => (
              <button
                key={s.id}
                onClick={() => setActiveSession(s.id)}
                className="group flex flex-col gap-1 px-4 py-3 rounded-xl text-left transition-all"
                style={{
                  background: activeSession === s.id ? "rgba(255,255,255,0.08)" : "transparent",
                  border: activeSession === s.id ? "1px solid rgba(255,255,255,0.15)" : "1px solid transparent"
                }}
              >
                <div className="flex items-center justify-between">
                   <p style={{ color: activeSession === s.id ? "white" : "rgba(255,255,255,0.7)", fontSize: "14px", fontWeight: activeSession === s.id ? 700 : 500 }} className="truncate">
                    {s.title}
                  </p>
                </div>
                <div className="flex items-center gap-2 text-[11px]" style={{ color: "rgba(255,255,255,0.4)" }}>
                   <Calendar size={10} /> {new Date(s.created_at).toLocaleDateString(lang === "vi" ? "vi-VN" : "en-US")}
                </div>
              </button>
            ))}
          </div>
        </div>

        <div className="mt-auto p-4 border-t border-white/10">
           <button onClick={() => onNavigate("home")} className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-white/5" style={{ color: "rgba(255,255,255,0.6)", fontSize: "14px" }}>
            <Home size={17} /> {lang === "vi" ? "Về Trang Chủ" : "Back to Home"}
          </button>
        </div>
      </aside>

      {/* ── Main Chat Area ── */}
      <div className="flex-1 flex flex-col min-w-0 h-full relative">
        
        {/* Header */}
        <header className="flex items-center justify-between px-6 py-4 bg-white border-b border-[#F5CBA7] sticky top-0 z-10">
          <div className="flex items-center gap-4">
            <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="hidden lg:flex items-center justify-center p-2 rounded-xl hover:bg-orange-50 text-[#E2714A]">
              <Menu size={20} />
            </button>
            <button onClick={() => onNavigate("home")} className="lg:hidden flex items-center justify-center p-2 rounded-xl hover:bg-orange-50 text-[#E2714A]">
               <ArrowLeft size={20} />
            </button>
            <div>
              <h2 style={{ color: "#3D2314", fontWeight: 800, fontSize: "16px" }}>
                {activeSession ? sessions.find(s => s.id === activeSession)?.title : (lang === "vi" ? "AI Chat" : "AI Travel Assistant")}
              </h2>
              <p style={{ color: "#059669", fontSize: "11px", fontWeight: 600 }}>● {lang === "vi" ? "Sẵn sàng hỗ trợ" : "Assistant Online"}</p>
            </div>
          </div>
          <LangToggle lang={lang} setLang={setLang} />
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 lg:px-10 py-6 custom-scrollbar flex flex-col gap-4">
          {!activeSession ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center px-6">
               <div className="w-16 h-16 rounded-3xl flex items-center justify-center mb-6" style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)", boxShadow: "0 10px 30px rgba(226,113,74,0.3)" }}>
                  <Sparkles size={32} color="white" />
               </div>
               <h1 style={{ color: "#3D2314", fontSize: "24px", fontWeight: 900, marginBottom: "12px" }}>
                 {lang === "vi" ? "Bắt đầu cuộc trò chuyện mới" : "Plan Your Next Adventure"}
               </h1>
               <p style={{ color: "#7A4528", maxWidth: "400px", lineHeight: 1.6 }}>
                 {lang === "vi" ? "Hãy tạo một phiên chat mới để AI giúp bạn tìm kiếm quà lưu niệm, đặc sản và lên kế hoạch cho chuyến đi của mình." : "Create a new session to let AI help you find perfect souvenirs, local specialties, and plan your trip details."}
               </p>
               <button 
                 onClick={startNewSession}
                 className="mt-8 px-8 py-4 rounded-2xl transition-all hover:scale-105"
                 style={{ background: "#E2714A", color: "white", fontWeight: 700, boxShadow: "0 8px 25px rgba(226,113,74,0.3)" }}
               >
                 {lang === "vi" ? "Bắt đầu ngay" : "Start Chatting"}
               </button>
            </div>
          ) : (
            <>
              {messages.length === 0 && !isLoading && (
                 <div className="flex flex-col items-center justify-center py-20 text-center opacity-40">
                    <MessageCircle size={48} className="mb-4 text-[#7A4528]" />
                    <p style={{ color: "#3D2314", fontWeight: 600 }}>{lang === "vi" ? "Chưa có tin nhắn nào. Hãy bắt đầu hỏi AI!" : "No messages yet. Start asking AI!"}</p>
                 </div>
              )}
              {messages.map((msg, i) => (
                <div key={i} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                  {msg.sender === "ai" && (
                    <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mr-3 mt-1 shadow-sm" style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)" }}>
                      <Sparkles size={16} color="white" />
                    </div>
                  )}
                  <div
                    className="max-w-[85%] lg:max-w-[70%] px-5 py-3.5 shadow-sm"
                    style={{
                      background: msg.sender === "user" ? "#E2714A" : "white",
                      color: msg.sender === "user" ? "white" : "#3D2314",
                      borderRadius: msg.sender === "user" ? "24px 24px 4px 24px" : "24px 24px 24px 4px",
                      border: msg.sender === "user" ? "none" : "1px solid #F5CBA7"
                    }}
                  >
                    <div className="text-[14px] leading-relaxed">
                      {renderMessage(msg.text)}
                    </div>
                    <p className="mt-1.5 text-[10px] opacity-50 text-right">
                      {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                   <div className="w-8 h-8 rounded-xl flex items-center justify-center flex-shrink-0 mr-3 mt-1 shadow-sm" style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)" }}>
                      <Sparkles size={16} color="white" className="animate-pulse" />
                   </div>
                   <div className="px-5 py-4 rounded-[24px_24px_24px_4px] bg-white border border-[#F5CBA7] shadow-sm">
                      <div className="flex gap-1.5">
                         <div className="w-2 h-2 rounded-full bg-[#E2714A] animate-bounce" style={{ animationDelay: "0ms" }} />
                         <div className="w-2 h-2 rounded-full bg-[#E2714A] animate-bounce" style={{ animationDelay: "150ms" }} />
                         <div className="w-2 h-2 rounded-full bg-[#E2714A] animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                   </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </>
          )}
        </div>

        {/* Input */}
        {activeSession && (
          <div className="px-6 pb-8 pt-4 bg-transparent">
            <div className="max-w-4xl mx-auto flex items-center gap-3 p-2 pl-5 rounded-[28px] bg-white shadow-xl border-2 border-[#F5CBA7]">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                placeholder={lang === "vi" ? "Hỏi về đặc sản, quà tặng..." : "Ask about specialties, gifts..."}
                className="flex-1 outline-none bg-transparent py-2"
                style={{ color: "#3D2314", fontSize: "15px" }}
              />
              <button 
                onClick={sendMessage}
                disabled={!input.trim() || isLoading}
                className="w-12 h-12 flex items-center justify-center rounded-full transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:scale-100"
                style={{ background: "linear-gradient(135deg, #E2714A, #C8562E)", color: "white", boxShadow: "0 4px 15px rgba(226,113,74,0.3)" }}
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
