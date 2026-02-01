import { useRef, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';

interface Message3DProps {
  message: string;
  position: [number, number, number];
  isBot: boolean;
  timestamp: string;
  index: number;
}

export function Message3D({ message, position, isBot, timestamp, index }: Message3DProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = useState(false);

  useFrame((state) => {
    if (groupRef.current) {
      // Gentle floating animation
      groupRef.current.position.y = position[1] + Math.sin(state.clock.elapsedTime + index) * 0.1;
      
      // Gentle rotation
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.3 + index) * 0.05;

      // Pulse the scale when hovered
      const targetScale = hovered ? 1.05 : 1;
      groupRef.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), 0.1);
    }
  });

  const color = isBot ? '#ff006e' : '#00f3ff';
  const glowColor = isBot ? new THREE.Color('#ff006e') : new THREE.Color('#00f3ff');

  // Split long messages into multiple lines
  const maxLineLength = 40;
  const words = message.split(' ');
  let lines: string[] = [];
  let currentLine = '';

  words.forEach(word => {
    if ((currentLine + word).length > maxLineLength) {
      lines.push(currentLine.trim());
      currentLine = word + ' ';
    } else {
      currentLine += word + ' ';
    }
  });
  if (currentLine) lines.push(currentLine.trim());

  const displayText = lines.join('\n');

  return (
    <group position={position} ref={groupRef}>
      <mesh
        onPointerOver={() => setHovered(true)}
        onPointerOut={() => setHovered(false)}
      >
        {/* Message box */}
        <boxGeometry args={[3, 0.8 + lines.length * 0.3, 0.2]} />
        <meshStandardMaterial
          color={isBot ? '#1a0a1f' : '#0a1520'}
          emissive={glowColor}
          emissiveIntensity={hovered ? 0.3 : 0.15}
          transparent
          opacity={0.9}
        />
      </mesh>

      {/* Glowing edges */}
      <mesh position={[0, 0, 0]}>
        <boxGeometry args={[3.02, 0.82 + lines.length * 0.3, 0.22]} />
        <meshBasicMaterial
          color={color}
          transparent
          opacity={0.2}
          side={THREE.BackSide}
        />
      </mesh>

      {/* Message text */}
      <Text
        position={[0, 0, 0.11]}
        fontSize={0.12}
        color={color}
        anchorX="center"
        anchorY="middle"
        maxWidth={2.8}
        textAlign="left"
        font="https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTOlOVkw.woff"
      >
        {displayText}
      </Text>

      {/* Timestamp */}
      <Text
        position={[1.3, -0.35 - lines.length * 0.15, 0.11]}
        fontSize={0.06}
        color={color}
        anchorX="right"
        anchorY="middle"
        font="https://fonts.gstatic.com/s/jetbrainsmono/v18/tDbY2o-flEEny0FZhsfKu5WU4zr3E_BX0PnT8RD8yKxTOlOVkw.woff"
      >
        {timestamp}
      </Text>

      {/* Particle effects around the message */}
      {[...Array(8)].map((_, i) => (
        <Particle
          key={i}
          offset={i}
          color={color}
          radius={1.8}
        />
      ))}
    </group>
  );
}

function Particle({ offset, color, radius }: { offset: number; color: string; radius: number }) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      const angle = (offset / 8) * Math.PI * 2 + state.clock.elapsedTime * 0.5;
      meshRef.current.position.x = Math.cos(angle) * radius;
      meshRef.current.position.z = Math.sin(angle) * radius;
      meshRef.current.position.y = Math.sin(state.clock.elapsedTime * 2 + offset) * 0.2;
    }
  });

  return (
    <mesh ref={meshRef}>
      <sphereGeometry args={[0.02, 8, 8]} />
      <meshBasicMaterial color={color} transparent opacity={0.6} />
    </mesh>
  );
}
