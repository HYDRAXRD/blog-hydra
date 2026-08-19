import { categories } from '../../lib/blog';

interface CategoryFilterProps {
  active: string;
  onChange: (cat: string) => void;
}

export function CategoryFilter({ active, onChange }: CategoryFilterProps) {
  return (
    <nav aria-label="Filter by category" className="flex flex-wrap gap-2 mb-10">
      {categories.map((cat) => (
        <button
          key={cat}
          onClick={() => onChange(cat)}
          aria-pressed={active === cat}
          className={`text-[10px] font-bold tracking-[0.08em] uppercase px-4 py-2 rounded-full border transition-all duration-200 ${
            active === cat
              ? 'border-cyan-400 text-cyan-400 bg-cyan-500/10 shadow-[0_0_12px_rgba(0,210,255,0.2)]'
              : 'border-white/[0.08] text-white/40 bg-[#0a0c1a] hover:border-cyan-500/40 hover:text-cyan-400'
          }`}
        >
          {cat}
        </button>
      ))}
    </nav>
  );
}
