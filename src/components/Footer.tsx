import { Link } from "@tanstack/react-router";
import hydraLogo from "@/assets/hydraxrd-logo.png";

const Footer = () => {
  return (
    <footer className="border-t border-border/50 bg-card/30 py-12">
      <div className="container-hydra">
        <div className="mb-8 grid gap-8 md:grid-cols-4">
          <div>
            <div className="mb-4 flex items-center gap-2">
              <img src={hydraLogo} alt="HYDRA logo" className="h-8 w-8 object-contain" />
              <span className="font-display text-lg font-bold">HYDRA</span>
            </div>
            <p className="text-sm leading-relaxed text-muted-foreground">
              Memecoin news, moonshot breakdowns and market analysis from the HYDRA community.
              WE ARE HYDRA! 🐉
            </p>
          </div>

          <div>
            <h2 className="mb-4 font-display text-sm font-bold">Hydra Ecosystem</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <a href="https://hydraxrd.com/swap" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">HydraSwap</a>
              </li>
              <li>
                <a href="https://hydraxrd.com/bubbles" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">HydraBubbles</a>
              </li>
              <li>
                <a href="https://hydraxrd.com/burn" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">HydraBurn</a>
              </li>
              <li>
                <a href="https://hydraxrd.com/battlearena" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">HydraBattlearena</a>
              </li>
              <li>
                <a href="https://hydraxrd.com/track" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">HydraTrack</a>
              </li>
              <li>
                <Link to="/" className="transition-colors hover:text-primary">HydraBlog</Link>
              </li>
            </ul>
          </div>

          <div>
            <h2 className="mb-4 font-display text-sm font-bold">Radix Ecosystem</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="https://www.radixdlt.com" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">Radix DLT</a></li>
              <li><a href="https://dashboard.radixdlt.com" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">Radix Dashboard</a></li>
              <li><a href="https://www.radixdlt.com/wallet" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">Radix Wallet</a></li>
              <li><a href="https://developers.radixdlt.com" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">Developer Docs</a></li>
            </ul>
          </div>

          <div>
            <h2 className="mb-4 font-display text-sm font-bold">Follow Us</h2>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li><a href="https://x.com/HYDRAXRD" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">X</a></li>
              <li><a href="https://t.me/hydraxrd" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">Telegram</a></li>
              <li><a href="https://www.instagram.com/hydraxrd" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">Instagram</a></li>
              <li><a href="https://www.tiktok.com/@hydraxrd" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">TikTok</a></li>
              <li><a href="https://www.youtube.com/@HYDRAXRD" target="_blank" rel="noopener noreferrer" className="transition-colors hover:text-primary">YouTube</a></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-border/50 pt-6">
          <p className="max-w-3xl text-xs leading-relaxed text-muted-foreground">
            Disclaimer: HYDRA is a community-driven memecoin project. Nothing published on this
            blog is financial advice. Cryptocurrency investments carry risk. Always do your own
            research before investing. HYDRA is not affiliated with or endorsed by Radix DLT Ltd.
          </p>
          <p className="mt-4 text-xs text-muted-foreground">
            © {new Date().getFullYear()} HYDRA. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
