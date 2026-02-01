import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function FloatingParticles() {
  const particlesRef = useRef<THREE.Points>(null);

  const particles = useMemo(() => {
    const count = 500;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const speeds = new Float32Array(count);

    const color1 = new THREE.Color('#00f3ff');
    const color2 = new THREE.Color('#ff006e');
    const color3 = new THREE.Color('#9d4edd');

    for (let i = 0; i < count; i++) {
      const i3 = i * 3;

      // Random position in a large sphere
      positions[i3] = (Math.random() - 0.5) * 50;
      positions[i3 + 1] = (Math.random() - 0.5) * 30;
      positions[i3 + 2] = (Math.random() - 0.5) * 50;

      // Random color
      const colorChoice = Math.random();
      const chosenColor = colorChoice < 0.33 ? color1 : colorChoice < 0.66 ? color2 : color3;
      colors[i3] = chosenColor.r;
      colors[i3 + 1] = chosenColor.g;
      colors[i3 + 2] = chosenColor.b;

      // Random speed
      speeds[i] = Math.random() * 0.5 + 0.2;
    }

    return { positions, colors, speeds };
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position.array as Float32Array;

      for (let i = 0; i < positions.length; i += 3) {
        const speedIndex = i / 3;
        
        // Floating movement
        positions[i + 1] += Math.sin(state.clock.elapsedTime * particles.speeds[speedIndex]) * 0.01;
        
        // Gentle drift
        positions[i] += Math.cos(state.clock.elapsedTime * 0.1 + speedIndex) * 0.005;
        positions[i + 2] += Math.sin(state.clock.elapsedTime * 0.1 + speedIndex) * 0.005;
      }

      particlesRef.current.geometry.attributes.position.needsUpdate = true;
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.05;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.positions.length / 3}
          array={particles.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particles.colors.length / 3}
          array={particles.colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}
