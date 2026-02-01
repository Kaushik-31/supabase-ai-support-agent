import { Send, Navigation, Maximize2, Minimize2 } from 'lucide-react';
import { motion } from 'motion/react';
import { useState } from 'react';

interface HUDOverlayProps {
  inputValue: string;
  setInputValue: (value: string) => void;
  onSend: () => void;
  isTyping: boolean;
}

export function HUDOverlay({ inputValue, setInputValue, onSend, isTyping }: HUDOverlayProps) {
  const [isFocused, setIsFocused] = useState(false);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSend();
    }
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyPress={handleKeyPress}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        placeholder="Enter neural command..."
        className="w-full bg-transparent border-b-2 px-4 py-3 pr-12 outline-none transition-all text-sm"
        style={{
          borderColor: isFocused ? '#00f3ff' : 'rgba(0, 243, 255, 0.3)',
          color: '#00f3ff',
          fontFamily: "'JetBrains Mono', monospace",
          textShadow: '0 0 10px rgba(0, 243, 255, 0.3)',
        }}
      />

      <motion.div
        className="absolute bottom-0 left-0 h-[2px]"
        style={{
          background: 'linear-gradient(90deg, #00f3ff, #9d4edd, #ff006e)',
          width: '100%',
          transformOrigin: 'left',
        }}
        animate={{
          scaleX: isFocused ? 1 : 0,
        }}
        transition={{
          duration: 0.3,
        }}
      />

      <button
        onClick={onSend}
        className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-lg transition-all hover:scale-110"
        style={{
          background: 'rgba(0, 243, 255, 0.1)',
          border: '1px solid rgba(0, 243, 255, 0.5)',
          color: '#00f3ff',
          boxShadow: '0 0 15px rgba(0, 243, 255, 0.3)',
        }}
      >
        <Send size={16} />
      </button>
    </div>
  );
}
