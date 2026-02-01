import { useEffect, useState } from 'react';

interface MatrixChar {
  id: number;
  char: string;
  left: number;
  duration: number;
  delay: number;
  fontSize: number;
}

export function MatrixRain() {
  const [chars, setChars] = useState<MatrixChar[]>([]);

  useEffect(() => {
    const characters = '01アイウエオカキクケコサシスセソタチツテトナニヌネノ<>{}[]';
    const newChars: MatrixChar[] = [];

    // Create 30 falling characters
    for (let i = 0; i < 30; i++) {
      newChars.push({
        id: i,
        char: characters[Math.floor(Math.random() * characters.length)],
        left: Math.random() * 100,
        duration: 10 + Math.random() * 15,
        delay: Math.random() * 5,
        fontSize: 12 + Math.random() * 8,
      });
    }

    setChars(newChars);
  }, []);

  return (
    <div className="fixed inset-0 overflow-hidden pointer-events-none" style={{ zIndex: 0 }}>
      {chars.map((char) => (
        <div
          key={char.id}
          className="matrix-char"
          style={{
            left: `${char.left}%`,
            fontSize: `${char.fontSize}px`,
            animationDuration: `${char.duration}s`,
            animationDelay: `${char.delay}s`,
          }}
        >
          {char.char}
        </div>
      ))}
    </div>
  );
}
