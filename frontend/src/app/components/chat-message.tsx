import { motion } from 'motion/react';
import { ThumbsUp, ThumbsDown } from 'lucide-react';
import { BotAvatar } from './bot-avatar';
import { useState } from 'react';

interface ChatMessageProps {
  message: string;
  isBot: boolean;
  timestamp: string;
  showFeedback?: boolean;
  conversationId?: number;
}

export function ChatMessage({ message, isBot, timestamp, showFeedback, conversationId }: ChatMessageProps) {
  const [feedback, setFeedback] = useState<'up' | 'down' | null>(null);
  const [feedbackSent, setFeedbackSent] = useState(false);

  const handleFeedback = async (type: 'up' | 'down') => {
    if (feedbackSent || !conversationId) return;

    setFeedback(type);

    try {
      const response = await fetch('/feedback', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          conversation_id: conversationId,
          rating: type === 'up' ? 1 : -1,
        }),
      });

      if (response.ok) {
        setFeedbackSent(true);
      }
    } catch (error) {
      console.error('Failed to send feedback:', error);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`flex gap-3 mb-6 ${isBot ? 'justify-start' : 'justify-end'}`}
    >
      {isBot && (
        <div className="flex-shrink-0 mt-1">
          <BotAvatar />
        </div>
      )}

      <div className={`flex flex-col ${isBot ? 'items-start' : 'items-end'} max-w-[70%]`}>
        <motion.div
          className={`relative px-5 py-3 rounded-lg backdrop-blur-sm ${
            isBot
              ? 'bg-[#1a0a1f]/60 border border-[#ff006e]/50'
              : 'bg-[#0a1520]/60 border border-[#00f3ff]/50'
          } pulse-glow holographic`}
          style={{
            color: isBot ? '#ff006e' : '#00f3ff',
            boxShadow: isBot
              ? '0 0 20px rgba(255, 0, 110, 0.3)'
              : '0 0 20px rgba(0, 243, 255, 0.3)',
          }}
        >
          <p className="text-sm leading-relaxed whitespace-pre-wrap" style={{
            fontFamily: "'JetBrains Mono', monospace",
            textShadow: isBot
              ? '0 0 10px rgba(255, 0, 110, 0.5)'
              : '0 0 10px rgba(0, 243, 255, 0.5)'
          }}>
            {message}
          </p>
        </motion.div>

        <div className="flex items-center gap-3 mt-2">
          <span
            className="text-[10px] opacity-50"
            style={{
              fontFamily: "'JetBrains Mono', monospace",
              color: isBot ? '#ff006e' : '#00f3ff',
              textShadow: isBot
                ? '0 0 5px rgba(255, 0, 110, 0.3)'
                : '0 0 5px rgba(0, 243, 255, 0.3)'
            }}
          >
            {timestamp}
          </span>

          {showFeedback && isBot && (
            <div className="flex gap-2">
              <button
                onClick={() => handleFeedback('up')}
                disabled={feedbackSent}
                className={`p-1 rounded transition-all ${
                  feedback === 'up'
                    ? 'text-[#00f3ff]'
                    : 'text-gray-600 hover:text-[#00f3ff]'
                } ${feedbackSent ? 'opacity-50 cursor-not-allowed' : ''}`}
                style={{
                  textShadow: feedback === 'up' ? '0 0 8px rgba(0, 243, 255, 0.8)' : 'none'
                }}
              >
                <ThumbsUp size={12} />
              </button>
              <button
                onClick={() => handleFeedback('down')}
                disabled={feedbackSent}
                className={`p-1 rounded transition-all ${
                  feedback === 'down'
                    ? 'text-[#ff006e]'
                    : 'text-gray-600 hover:text-[#ff006e]'
                } ${feedbackSent ? 'opacity-50 cursor-not-allowed' : ''}`}
                style={{
                  textShadow: feedback === 'down' ? '0 0 8px rgba(255, 0, 110, 0.8)' : 'none'
                }}
              >
                <ThumbsDown size={12} />
              </button>
            </div>
          )}
        </div>
      </div>

      {!isBot && (
        <div className="flex-shrink-0 mt-1">
          <div
            className="w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold"
            style={{
              background: 'linear-gradient(135deg, #00f3ff, #0088ff)',
              boxShadow: '0 0 20px rgba(0, 243, 255, 0.5)',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            U
          </div>
        </div>
      )}
    </motion.div>
  );
}
