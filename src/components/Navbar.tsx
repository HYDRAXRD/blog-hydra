import { useState } from "react";
import { Menu, X } from "lucide-react";
import { Link } from "@tanstack/react-router";
import hydraLogo from "@/assets/hydraxrd-logo.png";

const navLinks = [
  { label: "Home", href: "https://hydraxrd.com/" },
  { label: "About", href: "https://hydraxrd.com/#about" },
  { label: "Game", href: "https://hydraxrd.com/#game" },
  { label: "Roadmap", href: "https://hydraxrd.com/#roadmap" },
  { label: "Tokenomics", href: "https://hydraxrd.com/#tokenomics" },
  { label: "Community", href: "https://hydraxrd.com/#community" },
];

const Navbar = () => {
  const [open, setOpen] = useState(false);

  return (
    <nav className="fixed top-0 right-0 left-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
      <div className="container-hydra flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2 transition-transform hover:scale-105">
          <img src={hydraLogo} alt="HYDRA logo" className="h-10 w-10 object-contain" />
          <span className="font-display text-lg font-bold text-glow">HYDRA</span>
          <span className="hidden font-display text-lg font-bold text-accent text-glow-green sm:inline">
            /BLOG
          </span>
        </Link>

        <div className="hidden items-center gap-6 md:flex">
          {navLinks.map((l) => (
            <a
              key={l.label}
              href={l.href}
              className="text-sm font-medium text-muted-foreground transition-colors hover:text-primary"
            >
              {l.label}
            </a>
          ))}
          <Link
            to="/"
            className="text-sm font-medium text-primary transition-colors hover:text-accent"
          >
            Blog
          </Link>
          <a
            href="https://hydraxrd.com/swap"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex animate-pulse items-center gap-2 rounded-lg bg-gradient-to-r from-primary via-accent to-destructive px-4 py-2 text-sm font-bold text-primary-foreground shadow-lg shadow-primary/30 transition-shadow hover:shadow-primary/50"
          >
            🐉 Buy Now 🔥
          </a>
        </div>

        <button
          className="text-foreground md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Toggle menu"
        >
          {open ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {open && (
        <div className="border-t border-border/50 bg-background/95 backdrop-blur-xl md:hidden">
          {navLinks.map((l) => (
            <a
              key={l.label}
              href={l.href}
              className="block px-6 py-3 text-sm text-muted-foreground transition-colors hover:text-primary"
            >
              {l.label}
            </a>
          ))}
          <div className="px-6 py-3">
            <a
              href="https://hydraxrd.com/swap"
              target="_blank"
              rel="noopener noreferrer"
              className="block rounded-lg bg-gradient-to-r from-primary via-accent to-destructive px-4 py-2 text-center text-sm font-bold text-primary-foreground shadow-lg shadow-primary/30"
            >
              🐉 Buy Now 🔥
            </a>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
