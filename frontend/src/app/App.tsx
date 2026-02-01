import { useState, useEffect, useRef } from 'react';
import { HUDOverlay } from './components/hud-overlay';
import { GlitchArtifacts } from './components/glitch-artifact';
import { MatrixRain } from './components/matrix-rain';
import { BotAvatar } from './components/bot-avatar';
import { ChatMessage } from './components/chat-message';

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: string;
  conversationId?: number;
}

interface Stats {
  online: boolean;
  queries_today: number;
  avg_response_time_ms: number;
}

export default function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Neural connection established. I'm your Supabase support agent. Ask me anything about authentication, databases, storage, or getting started with Supabase.",
      isBot: true,
      timestamp: new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [stats, setStats] = useState<Stats>({ online: false, queries_today: 0, avg_response_time_ms: 0 });
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Fetch stats on mount
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      }
    };
    fetchStats();
    const interval = setInterval(fetchStats, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMessage: Message = {
      id: Date.now(),
      text: inputValue,
      isBot: false,
      timestamp: new Date().toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      }),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsTyping(true);

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ message: inputValue }),
      });

      const data = await response.json();

      const botMessage: Message = {
        id: Date.now(),
        text: data.response || data.error || 'Sorry, I encountered an error.',
        isBot: true,
        timestamp: new Date().toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }),
        conversationId: data.conversation_id,
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now(),
        text: 'Connection error. Please check if the server is running.',
        isBot: true,
        timestamp: new Date().toLocaleTimeString('en-US', {
          hour12: false,
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit'
        }),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <div
      className="size-full overflow-hidden relative scanlines digital-noise"
      style={{
        background: '#0a0a0f',
        fontFamily: "'JetBrains Mono', monospace",
      }}
    >
      {/* Matrix rain background */}
      <div className="absolute inset-0 opacity-20">
        <MatrixRain />
      </div>

      {/* Animated grid background */}
      <div className="absolute inset-0 opacity-10">
        <div className="cyberpunk-grid" />
      </div>

      {/* Main content */}
      <div className="relative z-10 size-full flex flex-col">
        {/* Header */}
        <div className="p-6 border-b border-[#00f3ff]/30 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-[#00f3ff]/5 to-[#ff006e]/5" />
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-4">
              <BotAvatar />
              <div>
                <h1 className="text-2xl font-bold glitch-text neon-text-blue tracking-wider">
                  SUPABASE NEURAL AGENT
                </h1>
                <p className="text-sm text-[#9d4edd] mt-1">
                  [ QUANTUM INTERFACE v2.077 ]
                </p>
              </div>
            </div>
            <div className="flex items-center gap-6 text-xs">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${stats.online ? 'bg-[#00ff88] animate-pulse' : 'bg-red-500'}`} />
                <span className="text-[#00f3ff]">{stats.online ? 'ONLINE' : 'OFFLINE'}</span>
              </div>
              <div className="text-[#9d4edd]">
                QUERIES TODAY: <span className="text-[#00f3ff]">{stats.queries_today}</span>
              </div>
              <div className="text-[#9d4edd]">
                AVG RESPONSE: <span className="text-[#00f3ff]">{(stats.avg_response_time_ms / 1000).toFixed(1)}s</span>
              </div>
            </div>
          </div>
        </div>

        {/* Chat messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4 custom-scrollbar">
          {messages.map((msg) => (
            <ChatMessage
              key={msg.id}
              message={msg.text}
              isBot={msg.isBot}
              timestamp={msg.timestamp}
              showFeedback={msg.isBot && msg.conversationId !== undefined}
              conversationId={msg.conversationId}
            />
          ))}

          {isTyping && (
            <div className="flex gap-3">
              <div className="size-10 rounded-full bg-gradient-to-br from-[#ff006e] to-[#9d4edd] p-[2px] shrink-0">
                <div className="size-full rounded-full bg-[#0a0a0f] flex items-center justify-center">
                  <div className="w-6 h-6 relative">
                    <div className="absolute inset-0 bg-[#ff006e] rounded-full animate-ping opacity-75" />
                    <div className="relative size-full bg-gradient-to-br from-[#ff006e] to-[#9d4edd] rounded-full" />
                  </div>
                </div>
              </div>
              <div className="flex-1">
                <div className="inline-block px-6 py-4 rounded-lg bg-gradient-to-br from-[#1a0a1f] to-[#0a0a0f] border-2 border-[#ff006e]/50 neon-border-pink">
                  <div className="flex gap-2">
                    <span className="w-2 h-2 rounded-full bg-[#ff006e] animate-pulse" />
                    <span className="w-2 h-2 rounded-full bg-[#ff006e] animate-pulse" style={{ animationDelay: '0.2s' }} />
                    <span className="w-2 h-2 rounded-full bg-[#ff006e] animate-pulse" style={{ animationDelay: '0.4s' }} />
                  </div>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input area */}
        <div className="p-6 border-t border-[#00f3ff]/30 relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-t from-[#00f3ff]/5 to-transparent" />
          <div className="relative">
            <HUDOverlay
              inputValue={inputValue}
              setInputValue={setInputValue}
              onSend={handleSend}
              isTyping={isTyping}
            />
          </div>
        </div>
      </div>

      {/* Glitch artifacts */}
      <GlitchArtifacts />

      {/* Vignette effect */}
      <div
        className="absolute inset-0 pointer-events-none"
        style={{
          background: 'radial-gradient(ellipse at center, transparent 0%, rgba(10, 10, 15, 0.6) 100%)',
          zIndex: 5,
        }}
      />

      {/* Floating particles */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {[...Array(30)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 rounded-full"
            style={{
              background: i % 3 === 0 ? '#00f3ff' : i % 3 === 1 ? '#ff006e' : '#9d4edd',
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animation: `float ${5 + Math.random() * 10}s linear infinite`,
              animationDelay: `${Math.random() * 5}s`,
              opacity: 0.3,
            }}
          />
        ))}
      </div>

      <style>{`
        .cyberpunk-grid {
          width: 100%;
          height: 100%;
          background-image:
            linear-gradient(0deg, transparent 24%, rgba(0, 243, 255, 0.05) 25%, rgba(0, 243, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(255, 0, 110, 0.05) 75%, rgba(255, 0, 110, 0.05) 76%, transparent 77%, transparent),
            linear-gradient(90deg, transparent 24%, rgba(0, 243, 255, 0.05) 25%, rgba(0, 243, 255, 0.05) 26%, transparent 27%, transparent 74%, rgba(255, 0, 110, 0.05) 75%, rgba(255, 0, 110, 0.05) 76%, transparent 77%, transparent);
          background-size: 50px 50px;
          animation: gridScroll 20s linear infinite;
        }

        @keyframes gridScroll {
          0% {
            background-position: 0 0;
          }
          100% {
            background-position: 50px 50px;
          }
        }

        .scanlines {
          position: relative;
        }

        .scanlines::before {
          content: '';
          position: absolute;
          inset: 0;
          background: linear-gradient(
            transparent 50%,
            rgba(0, 243, 255, 0.02) 50%
          );
          background-size: 100% 4px;
          pointer-events: none;
          z-index: 100;
        }

        .digital-noise {
          position: relative;
        }

        .digital-noise::after {
          content: '';
          position: absolute;
          inset: 0;
          background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
          opacity: 0.03;
          pointer-events: none;
          animation: noise 0.2s infinite;
          z-index: 99;
        }

        @keyframes noise {
          0%, 100% { transform: translate(0, 0); }
          10% { transform: translate(-5%, -5%); }
          20% { transform: translate(-10%, 5%); }
          30% { transform: translate(5%, -10%); }
          40% { transform: translate(-5%, 15%); }
          50% { transform: translate(-10%, 5%); }
          60% { transform: translate(15%, 0); }
          70% { transform: translate(0, 10%); }
          80% { transform: translate(-15%, 0); }
          90% { transform: translate(10%, 5%); }
        }

        .glitch-text {
          position: relative;
          animation: glitch 3s infinite;
        }

        @keyframes glitch {
          0%, 90%, 100% {
            transform: translate(0);
          }
          91% {
            transform: translate(-2px, 2px);
          }
          92% {
            transform: translate(2px, -2px);
          }
          93% {
            transform: translate(-2px, 2px);
          }
        }

        .neon-text-blue {
          color: #00f3ff;
          text-shadow:
            0 0 5px #00f3ff,
            0 0 10px #00f3ff,
            0 0 20px #00f3ff,
            0 0 40px #00f3ff;
        }

        .neon-border-blue {
          box-shadow:
            0 0 5px #00f3ff,
            0 0 10px #00f3ff,
            inset 0 0 5px #00f3ff;
        }

        .neon-border-pink {
          box-shadow:
            0 0 5px #ff006e,
            0 0 10px #ff006e,
            inset 0 0 5px #ff006e;
        }

        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }

        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(0, 243, 255, 0.05);
        }

        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: linear-gradient(to bottom, #00f3ff, #ff006e);
          border-radius: 4px;
        }

        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: linear-gradient(to bottom, #ff006e, #9d4edd);
        }

        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
          }
          25% {
            transform: translateY(-20px) translateX(10px);
          }
          50% {
            transform: translateY(-40px) translateX(-10px);
          }
          75% {
            transform: translateY(-20px) translateX(5px);
          }
        }
      `}</style>
    </div>
  );
}
