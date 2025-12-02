'use client';

import { Button } from '@/components/livekit/button';
import { cn } from '@/lib/utils';
import { useEffect, useState } from 'react';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div ref={ref} className="relative min-h-screen w-full overflow-hidden bg-[#0a0506]">
      {/* Animated gradient background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a0a0f] via-[#2d1410] to-[#0a0506]" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYgMi42ODYgNiA2cy0yLjY4NiA2LTYgNi02LTIuNjg2LTYtNiAyLjY4Ni02IDYtNnoiIHN0cm9rZT0icmdiYSgyNTUsIDIxNSwgMCwgMC4wMykiLz48L2c+PC9zdmc+')] opacity-30" />
      </div>

      {/* Glowing orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#d4751a] rounded-full blur-[120px] opacity-20 animate-pulse" />
      <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#ffd700] rounded-full blur-[100px] opacity-15 animate-pulse" style={{ animationDelay: '1s' }} />

      {/* Main content */}
      <div className={cn(
        "relative z-10 flex min-h-screen flex-col items-center justify-center px-6 py-12",
        "transition-all duration-1000",
        mounted ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"
      )}>
        {/* Top badge */}
        <div className="mb-8 flex items-center gap-2 rounded-full border border-[#d4751a]/30 bg-[#d4751a]/10 px-4 py-2 backdrop-blur-sm">
          <div className="w-2 h-2 rounded-full bg-[#ffd700] animate-pulse" />
          <span className="text-sm font-medium text-[#ffd700] tracking-wider">VOICE RPG EXPERIENCE</span>
        </div>

        {/* Main title section */}
        <div className="max-w-4xl text-center space-y-6">
          {/* Om symbol */}
          <div className="text-6xl mb-4 animate-pulse" style={{ color: '#ffd700' }}>
            ॐ
          </div>

          {/* Title */}
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight">
            <span className="bg-gradient-to-r from-[#ffd700] via-[#ff8c00] to-[#d4751a] bg-clip-text text-transparent">
              RAMAYAN
            </span>
          </h1>

          {/* Subtitle */}
          <p className="text-2xl md:text-3xl font-semibold text-[#c9a961] tracking-wide">
            Sundara Kanda
          </p>

          {/* Description */}
          <p className="text-lg md:text-xl text-[#f5e6d3]/80 max-w-2xl mx-auto leading-relaxed">
            Play as <span className="text-[#ffd700] font-semibold">Hanuman</span> in an epic voice-driven adventure. 
            Journey to <span className="text-[#ff8c00] font-semibold">Lanka</span>, find <span className="text-[#ffd700] font-semibold">Sita</span>, 
            and shape the story with your choices.
          </p>

          {/* Features */}
          <div className="flex flex-wrap justify-center gap-6 pt-4 text-sm text-[#f5e6d3]/70">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-[#d4751a]" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"/>
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd"/>
              </svg>
              <span>Voice-Only Gameplay</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-[#d4751a]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
              <span>15-Turn Story Arc</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-[#d4751a]" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd"/>
              </svg>
              <span>Your Choices Matter</span>
            </div>
          </div>

          {/* CTA Button */}
          <div className="pt-8">
            <Button
              onClick={onStartCall}
              className={cn(
                "group relative overflow-hidden rounded-full px-12 py-6 text-lg font-bold",
                "bg-gradient-to-r from-[#d4751a] to-[#ff8c00]",
                "hover:from-[#ff8c00] hover:to-[#ffd700]",
                "shadow-[0_0_40px_rgba(212,117,26,0.4)]",
                "hover:shadow-[0_0_60px_rgba(255,215,0,0.6)]",
                "transition-all duration-300 transform hover:scale-105",
                "text-[#0a0506] tracking-wider"
              )}
            >
              <span className="relative z-10 flex items-center gap-3">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd"/>
                </svg>
                BEGIN YOUR QUEST
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-200%] group-hover:translate-x-[200%] transition-transform duration-1000" />
            </Button>
          </div>

          {/* Bottom info */}
          <p className="text-sm text-[#f5e6d3]/50 pt-4">
            🎤 Microphone required • 🎧 Headphones recommended
          </p>
        </div>

        {/* Decorative elements */}
        <div className="absolute top-8 left-8 text-[#d4751a]/20 text-6xl font-bold">
          ॐ
        </div>
        <div className="absolute bottom-8 right-8 text-[#d4751a]/20 text-6xl font-bold">
          ॐ
        </div>
      </div>

      {/* Bottom accent line */}
      <div className="absolute bottom-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[#ffd700] to-transparent opacity-50" />
    </div>
  );
};
