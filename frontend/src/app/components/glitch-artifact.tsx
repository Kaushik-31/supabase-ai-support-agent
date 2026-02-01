import { useEffect, useState } from 'react';

interface Artifact {
  id: number;
  top: number;
  left: number;
  width: number;
  height: number;
}

export function GlitchArtifacts() {
  const [artifacts, setArtifacts] = useState<Artifact[]>([]);

  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly show glitch artifacts
      if (Math.random() > 0.7) {
        const newArtifact: Artifact = {
          id: Date.now(),
          top: Math.random() * 80 + 10,
          left: Math.random() * 80 + 10,
          width: Math.random() * 100 + 50,
          height: 2 + Math.random() * 4,
        };

        setArtifacts(prev => [...prev, newArtifact]);

        // Remove after animation
        setTimeout(() => {
          setArtifacts(prev => prev.filter(a => a.id !== newArtifact.id));
        }, 300);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none" style={{ zIndex: 50 }}>
      {artifacts.map((artifact) => (
        <div
          key={artifact.id}
          className="glitch-artifact"
          style={{
            top: `${artifact.top}%`,
            left: `${artifact.left}%`,
            width: `${artifact.width}px`,
            height: `${artifact.height}px`,
          }}
        />
      ))}
    </div>
  );
}
