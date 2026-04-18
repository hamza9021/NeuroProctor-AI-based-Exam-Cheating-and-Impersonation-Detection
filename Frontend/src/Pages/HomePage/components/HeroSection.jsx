import React from 'react';
import bgImg from '../../../assets/bg_img.png';
import { useNavigate } from 'react-router-dom';

export default function HeroSection() {
  const navigate = useNavigate();

  return (
    <section className="relative w-full h-screen overflow-hidden shrink-0">

      {/* Centered Background Image */}
      <div className="absolute inset-0 w-full h-full pointer-events-none flex items-center justify-center z-10 mix-blend-screen">
        <img
          src={bgImg}
          alt="Particle Face"
          className="w-full lg:w-[96%] h-[95%] object-cover object-center scale-105 animate-fade-in"
        />
      </div>

      {/* Foreground UI Overlay */}
      <div className="absolute inset-6 md:inset-10 z-30 pointer-events-none flex flex-col justify-between mix-blend-difference">

        {/* Top Tier */}
        <div className="flex justify-between items-start w-full opacity-0 animate-fade-in-up">

          {/* Logo */}
          <div className="relative pointer-events-auto flex items-center group cursor-pointer transition-opacity opacity-90 hover:opacity-100">
            <div className="w-[1.5px] h-[75%] bg-white/50 mr-4 relative hidden sm:block">
              <div className="absolute top-[-2px] left-[-1.5px] w-[4px] h-[4px] bg-white shadow-[0_0_8px_rgba(255,255,255,0.8)] rounded-full"></div>
              <div className="absolute bottom-[-2px] left-[-1.5px] w-[4px] h-[4px] bg-white rounded-full"></div>
            </div>
            <div
              className="flex items-center gap-4 px-6 md:px-8 py-3 md:py-3.5 bg-white/5 hover:bg-white/10 backdrop-blur-md transition-all duration-300 text-white/80 hover:text-white"
              style={{ clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))' }}
            >
              <span className="text-[10px] md:text-xs uppercase tracking-[0.3em] font-bold transition-colors" style={{ fontFamily: "'Space Grotesk', sans-serif" }}>NEURO PROCTOR</span>
              <span className="border-l border-white/20 pl-4 text-[10px] md:text-xs font-bold tracking-widest leading-none">NP</span>
            </div>
          </div>

          {/* Right link */}
          <div className="relative pointer-events-auto cursor-pointer group flex items-center gap-2.5 opacity-60 hover:opacity-100 transition-all duration-300">
            <div className="w-1.5 h-1.5 rounded-full bg-transparent border border-white/60 group-hover:bg-white transition-colors"></div>
            <div className="text-[9px] md:text-[10px] uppercase tracking-[0.2em] font-medium pt-[1px]">
              About the system
            </div>
          </div>

        </div>

        {/* Floating Headline — Left */}
        <div className="absolute left-[-20px] top-[100px] w-full pointer-events-none">
          <div className="max-w-[500px] ml-2 flex gap-4 md:gap-6 opacity-0 animate-fade-in-up animation-delay-200">
            <div className="text-[10px] opacity-60 font-medium tracking-widest pt-2 md:pt-4" style={{ fontFamily: "'Inter', sans-serif" }}>
              01/07
            </div>
            <div>
              <h1
                className="text-white leading-[0.85] tracking-tight mb-6 flex flex-col"
                style={{ fontFamily: "'Bebas Neue', sans-serif", fontSize: '6vw' }}
              >
                <span className="ml-[15%]">SECURING</span>
                <span>ACADEMIC</span>
                <span className="ml-[8%]">INTEGRITY</span>
              </h1>
              <p className="text-[10px] md:text-[11px] font-light tracking-widest opacity-80 leading-relaxed max-w-[320px]">
                Advanced AI exam cheating &amp; impersonation detection system.<br />
                <span className="text-[9px] md:text-[10px] text-white/50 mt-2 block tracking-widest font-normal">
                  Developed as a final year CS project by Muhammad Yousif, Adam Ali, and Hamza Riaz.
                </span>
              </p>
            </div>
          </div>
        </div>

        {/* Data Block — Right */}
        <div className="flex justify-end items-center w-full absolute top-[225px] right-[30px] flex-1 pointer-events-none">
          <div className="flex flex-col items-end gap-3 pointer-events-auto opacity-0 animate-fade-in-up animation-delay-400">
            <div className="text-right text-[9px] uppercase tracking-[0.3em] leading-loose opacity-60">
              Neural Precision
            </div>
            <div style={{ fontFamily: "'Orbitron', sans-serif" }} className="text-5xl md:text-8xl font-bold tracking-tighter">
              99.8<span className="text-2xl opacity-40 font-inter">%</span>
            </div>

            <div className="flex gap-4 mt-6 relative left-[40px]">
              {/* Get Started Button */}
              <button
                onClick={() => navigate('/invigilator/login')}
                className="relative flex items-center justify-center gap-3 px-6 py-3.5 bg-white/10 hover:bg-white/20 backdrop-blur-md transition-all duration-300 text-white group"
                style={{ clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))' }}
              >
                <span className="text-[10px] tracking-[0.25em] uppercase font-medium">Get Started</span>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="group-hover:translate-x-1 transition-transform">
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </button>

              {/* Learn More Button */}
              <button
                className="relative flex items-center justify-center gap-3 px-6 py-3.5 bg-white/5 hover:bg-white/10 backdrop-blur-md transition-all duration-300 text-white/80 hover:text-white group"
                style={{ clipPath: 'polygon(0 0, calc(100% - 10px) 0, 100% 10px, 100% 100%, 10px 100%, 0 calc(100% - 10px))' }}
              >
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="10"></circle>
                  <path d="M12 16v-4M12 8h.01"></path>
                </svg>
                <span className="text-[10px] tracking-[0.25em] uppercase font-medium">Learn More</span>
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Tier */}
        <div className="flex justify-between items-end w-full opacity-0 animate-fade-in-up animation-delay-600">
          {/* Protocol Tracker */}
          <div className="relative pointer-events-auto flex flex-col gap-1.5 opacity-50 hover:opacity-100 transition-opacity cursor-pointer">
            <div className="text-[6px] md:text-[7px] uppercase tracking-[0.5em] text-white/50 pl-0.5">
              System // Status
            </div>
            <div className="text-[8px] md:text-[9px] uppercase tracking-[0.4em] font-bold flex items-center gap-3">
              N-P // INITIATION PROTOCOL ACTIVE
              <span className="w-1.5 h-1.5 bg-white shadow-[0_0_8px_rgba(255,255,255,1)] rounded-full animate-pulse mb-[1px]"></span>
            </div>
          </div>

          {/* Navigation */}
          <div className="relative pointer-events-auto hidden md:block mr-[20px]">
            <div className="flex gap-[5px] h-[36px] relative" style={{ transform: 'skewX(-25deg)' }}>
              <div className="w-[6px] bg-white/10 backdrop-blur-md"></div>
              <div className="w-[6px] bg-white/10 backdrop-blur-md"></div>
              <div className="w-[6px] bg-white/10 backdrop-blur-md"></div>

              <nav className="pl-6 pr-10 bg-white/10 backdrop-blur-md flex items-center gap-10">
                {["Home", "Features", "How it Works", "Login"].map((item) => (
                  <a
                    key={item}
                    href={`#${item.toLowerCase().replace(/\s+/g, '-')}`}
                    className="text-[9px] uppercase tracking-[0.3em] font-medium text-white/70 hover:text-white transition-colors block"
                    style={{ fontFamily: "'DM Sans', sans-serif", transform: 'skewX(25deg)' }}
                  >
                    {item}
                  </a>
                ))}
              </nav>

              <div className="absolute top-[-7px] right-[-10px] w-[calc(100%+40px)] h-[calc(100%+11px)] pointer-events-none">
                <div className="absolute top-0 right-0 w-full flex items-center" style={{ transform: 'skewX(25deg)', transformOrigin: 'top right' }}>
                  <div className="w-[5px] h-[5px] bg-white/90 rounded-full"></div>
                  <div className="flex-1 h-[1px] bg-white/50 ml-1"></div>
                </div>
                <div className="absolute top-[3px] right-0 w-[1px] h-[100%] bg-white/50"></div>
                <div className="absolute bottom-[-2px] right-[-2px] w-[5px] h-[5px] bg-white/90 rounded-full" style={{ transform: 'skewX(25deg)' }}></div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
