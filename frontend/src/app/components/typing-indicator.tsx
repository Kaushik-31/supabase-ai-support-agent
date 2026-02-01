import { motion } from 'motion/react';
import { BotAvatar } from './bot-avatar';

export function TypingIndicator() {
  return (
    <div className="flex gap-3 mb-6 justify-start">
      <div className="flex-shrink-0 mt-1">
        <BotAvatar />
      </div>

      <div className="flex flex-col items-start">
        <div
          className="relative px-5 py-4 rounded-lg backdrop-blur-sm bg-[#1a0a1f]/60 border border-[#ff006e]/50 holographic"
          style={{
            boxShadow: '0 0 20px rgba(255, 0, 110, 0.3)',
          }}
        >
          <div className="flex gap-2 items-center">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2 h-2 rounded-full"
                style={{
                  background: '#ff006e',
                  boxShadow: '0 0 8px rgba(255, 0, 110, 0.8)',
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.5, 1, 0.5],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2,
                }}
              />
            ))}
            
            {/* Particle effects */}
            {[...Array(6)].map((_, i) => (
              <motion.div
                key={`particle-${i}`}
                className="absolute w-1 h-1 rounded-full"
                style={{
                  background: '#ff006e',
                  left: '50%',
                  top: '50%',
                }}
                animate={{
                  x: [0, (Math.random() - 0.5) * 30],
                  y: [0, (Math.random() - 0.5) * 30],
                  opacity: [0.8, 0],
                  scale: [1, 0],
                }}
                transition={{
                  duration: 1.5,
                  repeat: Infinity,
                  delay: i * 0.25,
                }}
              />
            ))}
          </div>
        </div>

        <span 
          className="text-[10px] opacity-50 mt-2"
          style={{ 
            fontFamily: "'JetBrains Mono', monospace",
            color: '#ff006e',
            textShadow: '0 0 5px rgba(255, 0, 110, 0.3)'
          }}
        >
          Processing neural network...
        </span>
      </div>
    </div>
  );
}
