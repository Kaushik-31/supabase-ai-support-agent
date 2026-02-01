import { motion } from 'motion/react';

export function BotAvatar() {
  return (
    <div className="relative w-10 h-10">
      {/* Central triangle */}
      <motion.div
        className="absolute inset-0"
        animate={{
          rotate: [0, 360],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear",
        }}
      >
        <svg width="40" height="40" viewBox="0 0 40 40">
          <polygon
            points="20,5 35,30 5,30"
            fill="none"
            stroke="#ff006e"
            strokeWidth="2"
            style={{
              filter: 'drop-shadow(0 0 8px rgba(255, 0, 110, 0.8))',
            }}
          />
        </svg>
      </motion.div>

      {/* Orbiting shards */}
      {[0, 120, 240].map((angle, i) => (
        <motion.div
          key={i}
          className="absolute"
          style={{
            top: '50%',
            left: '50%',
            marginTop: '-3px',
            marginLeft: '-3px',
          }}
          animate={{
            rotate: [angle, angle + 360],
            x: [
              Math.cos((angle * Math.PI) / 180) * 15,
              Math.cos(((angle + 360) * Math.PI) / 180) * 15,
            ],
            y: [
              Math.sin((angle * Math.PI) / 180) * 15,
              Math.sin(((angle + 360) * Math.PI) / 180) * 15,
            ],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: "linear",
          }}
        >
          <div
            className="w-1.5 h-1.5"
            style={{
              background: '#00f3ff',
              boxShadow: '0 0 6px rgba(0, 243, 255, 0.9)',
              clipPath: 'polygon(50% 0%, 100% 100%, 0% 100%)',
            }}
          />
        </motion.div>
      ))}
    </div>
  );
}
