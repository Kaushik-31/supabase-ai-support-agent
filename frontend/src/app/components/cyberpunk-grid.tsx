import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

export function CyberpunkGrid() {
  const gridRef = useRef<THREE.Group>(null);

  useFrame((state) => {
    if (gridRef.current) {
      // Animate grid slightly
      gridRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.1) * 0.01;
    }
  });

  return (
    <group ref={gridRef}>
      {/* Main grid - using mesh with custom geometry */}
      <GridMesh />

      {/* Horizontal glowing plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -5, 0]}>
        <planeGeometry args={[100, 100]} />
        <meshBasicMaterial
          color="#0a0a0f"
          transparent
          opacity={0.8}
          side={THREE.DoubleSide}
        />
      </mesh>

      {/* Neon accent lines */}
      {[...Array(10)].map((_, i) => (
        <NeonLine
          key={`line-${i}`}
          position={[i * 10 - 45, -4.9, 0]}
          color={i % 2 === 0 ? '#00f3ff' : '#ff006e'}
          offset={i}
        />
      ))}
    </group>
  );
}

function GridMesh() {
  const lineSegments = useMemo(() => {
    const size = 100;
    const divisions = 50;
    const step = size / divisions;
    const halfSize = size / 2;

    const vertices: number[] = [];
    const colors: number[] = [];

    const color1 = new THREE.Color('#00f3ff');
    const color2 = new THREE.Color('#9d4edd');

    for (let i = 0, j = 0, k = -halfSize; i <= divisions; i++, k += step) {
      // Lines parallel to X axis
      vertices.push(-halfSize, -5, k, halfSize, -5, k);
      
      // Alternate colors
      const color = i % 2 === 0 ? color1 : color2;
      colors.push(color.r, color.g, color.b);
      colors.push(color.r, color.g, color.b);

      // Lines parallel to Z axis
      vertices.push(k, -5, -halfSize, k, -5, halfSize);
      colors.push(color.r, color.g, color.b);
      colors.push(color.r, color.g, color.b);
    }

    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

    return geometry;
  }, []);

  const materialRef = useRef<THREE.LineBasicMaterial>(null);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.opacity = 0.3 + Math.sin(state.clock.elapsedTime * 0.5) * 0.1;
    }
  });

  return (
    <lineSegments geometry={lineSegments}>
      <lineBasicMaterial
        ref={materialRef}
        vertexColors
        transparent
        opacity={0.3}
      />
    </lineSegments>
  );
}

function NeonLine({ position, color, offset }: { position: [number, number, number]; color: string; offset: number }) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame((state) => {
    if (meshRef.current) {
      const material = meshRef.current.material as THREE.MeshBasicMaterial;
      material.opacity = 0.3 + Math.sin(state.clock.elapsedTime + offset) * 0.2;
    }
  });

  return (
    <mesh ref={meshRef} position={position} rotation={[Math.PI / 2, 0, 0]}>
      <boxGeometry args={[0.05, 100, 0.05]} />
      <meshBasicMaterial color={color} transparent opacity={0.5} />
    </mesh>
  );
}
