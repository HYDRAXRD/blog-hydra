import { useMemo } from "react";

/** Deterministic pseudo-random so SSR and client markup match exactly. */
const rand = (seed: number) => {
  const x = Math.sin(seed * 12.9898) * 43758.5453;
  return x - Math.floor(x);
};

const Particles = ({ count = 30 }: { count?: number }) => {
  const particles = useMemo(
    () =>
      Array.from({ length: count }, (_, i) => ({
        id: i,
        left: `${(rand(i + 1) * 100).toFixed(2)}%`,
        delay: `${(rand(i + 101) * 8).toFixed(2)}s`,
        duration: `${(6 + rand(i + 201) * 8).toFixed(2)}s`,
        size: `${(2 + rand(i + 301) * 4).toFixed(2)}px`,
        opacity: Number((0.3 + rand(i + 401) * 0.5).toFixed(2)),
      })),
    [count],
  );

  return (
    <div className="pointer-events-none absolute inset-0 overflow-hidden">
      {particles.map((p) => (
        <div
          key={p.id}
          className="particle"
          style={{
            left: p.left,
            bottom: "-10px",
            width: p.size,
            height: p.size,
            animationDelay: p.delay,
            animationDuration: p.duration,
            opacity: p.opacity,
          }}
        />
      ))}
    </div>
  );
};

export default Particles;
