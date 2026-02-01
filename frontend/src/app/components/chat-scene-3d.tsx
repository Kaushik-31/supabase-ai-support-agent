import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stars, PerspectiveCamera } from '@react-three/drei';
import { Message3D } from './message-3d';
import { CyberpunkGrid } from './cyberpunk-grid';
import { FloatingParticles } from './floating-particles';
import { BotAvatar3D } from './bot-avatar-3d';

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: string;
}

interface ChatScene3DProps {
  messages: Message[];
}

export function ChatScene3D({ messages }: ChatScene3DProps) {
  return (
    <Canvas
      camera={{ position: [0, 2, 10], fov: 75 }}
      style={{ width: '100%', height: '100%' }}
    >
      <PerspectiveCamera makeDefault position={[0, 2, 10]} fov={75} />
      
      {/* Lighting */}
      <ambientLight intensity={0.3} />
      <pointLight position={[10, 10, 10]} intensity={0.5} color="#00f3ff" />
      <pointLight position={[-10, 5, -10]} intensity={0.5} color="#ff006e" />
      <pointLight position={[0, -5, 0]} intensity={0.3} color="#9d4edd" />

      {/* Background stars */}
      <Stars
        radius={100}
        depth={50}
        count={5000}
        factor={4}
        saturation={0}
        fade
        speed={1}
      />

      {/* Cyberpunk grid floor */}
      <CyberpunkGrid />

      {/* Floating particles */}
      <FloatingParticles />

      {/* Bot avatar */}
      <BotAvatar3D />

      {/* Chat messages in 3D space */}
      {messages.map((message, index) => {
        // Arrange messages in a spiral pattern
        const radius = 8;
        const angleStep = (Math.PI * 2) / Math.max(messages.length, 8);
        const angle = index * angleStep;
        const heightStep = 1.5;
        
        const x = Math.cos(angle) * radius;
        const y = index * heightStep - (messages.length * heightStep) / 2 + 3;
        const z = Math.sin(angle) * radius;

        return (
          <Message3D
            key={message.id}
            message={message.text}
            position={[x, y, z]}
            isBot={message.isBot}
            timestamp={message.timestamp}
            index={index}
          />
        );
      })}

      {/* Camera controls - WASD + Mouse drag to navigate */}
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        rotateSpeed={0.5}
        panSpeed={0.5}
        zoomSpeed={0.5}
        minDistance={5}
        maxDistance={30}
        minPolarAngle={Math.PI / 6}
        maxPolarAngle={Math.PI / 1.5}
      />

      {/* Fog for depth */}
      <fog attach="fog" args={['#0a0a0f', 10, 50]} />
    </Canvas>
  );
}
