import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function BotAvatar3D() {
  const groupRef = useRef<THREE.Group>(null);
  const coreRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.3;
      groupRef.current.position.y = 2 + Math.sin(state.clock.elapsedTime) * 0.2;
    }

    if (coreRef.current) {
      coreRef.current.rotation.x = state.clock.elapsedTime * 0.5;
      coreRef.current.rotation.z = state.clock.elapsedTime * 0.3;
    }
  });

  return (
    <group ref={groupRef} position={[0, 2, -5]}>
      {/* Central core */}
      <mesh ref={coreRef}>
        <octahedronGeometry args={[0.5, 0]} />
        <meshStandardMaterial
          color="#ff006e"
          emissive="#ff006e"
          emissiveIntensity={0.5}
          wireframe
        />
      </mesh>

      {/* Inner glow */}
      <mesh>
        <octahedronGeometry args={[0.48, 0]} />
        <meshBasicMaterial
          color="#ff006e"
          transparent
          opacity={0.3}
        />
      </mesh>

      {/* Orbiting rings */}
      {[0, 60, 120].map((angle, i) => (
        <OrbitingRing
          key={i}
          radius={1.2}
          angle={angle}
          color="#00f3ff"
          speed={1 + i * 0.2}
        />
      ))}

      {/* Floating shards */}
      {[...Array(8)].map((_, i) => (
        <FloatingShard
          key={i}
          index={i}
          total={8}
        />
      ))}

      {/* Point light for glow */}
      <pointLight color="#ff006e" intensity={2} distance={5} />
    </group>
  );
}

function OrbitingRing({ radius, angle, color, speed }: { 
  radius: number; 
  angle: number; 
  color: string; 
  speed: number; 
}) {
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (ringRef.current) {
      ringRef.current.rotation.y = angle * (Math.PI / 180) + state.clock.elapsedTime * speed;
    }
  });

  return (
    <mesh ref={ringRef} rotation={[Math.PI / 2, 0, 0]}>
      <torusGeometry args={[radius, 0.02, 8, 32]} />
      <meshBasicMaterial color={color} transparent opacity={0.6} />
    </mesh>
  );
}

function FloatingShard({ index, total }: { index: number; total: number }) {
  const shardRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (shardRef.current) {
      const angle = (index / total) * Math.PI * 2 + state.clock.elapsedTime * 0.5;
      shardRef.current.position.x = Math.cos(angle) * 2;
      shardRef.current.position.z = Math.sin(angle) * 2;
      shardRef.current.position.y = Math.sin(state.clock.elapsedTime * 2 + index) * 0.5;
      shardRef.current.rotation.y = state.clock.elapsedTime * 2;
    }
  });

  return (
    <mesh ref={shardRef}>
      <coneGeometry args={[0.1, 0.3, 3]} />
      <meshStandardMaterial
        color="#9d4edd"
        emissive="#9d4edd"
        emissiveIntensity={0.5}
      />
    </mesh>
  );
}
