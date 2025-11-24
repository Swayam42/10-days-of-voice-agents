"use client";

import { forwardRef } from "react";
import { Button } from "@/components/livekit/button";
import Aurora from "@/components/ui/Aurora";
import SplitText from "@/components/ui/SplitText";

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = forwardRef<HTMLDivElement, WelcomeViewProps>(
  ({ startButtonText, onStartCall }, ref) => {
    return (
      <div ref={ref} className="relative w-full h-screen overflow-hidden">

        {/* Aurora Background */}
        <Aurora
          colorStops={["#7CFF67", "#B19EEF", "#5227FF"]}
          blend={0.5}
          amplitude={1}
          speed={1}
        />

        {/* Foreground UI */}
        <section className="absolute inset-0 flex flex-col items-center justify-center text-center gap-8">

          {/* SplitText Heading Animation */}
          <SplitText
            text="Your AI Health Companion"
            className="text-white text-4xl md:text-6xl font-bold drop-shadow-lg"
            delay={100}
            duration={0.6}
            ease="power3.out"
            from={{ opacity: 0, y: 40 }}
            to={{ opacity: 1, y: 0 }}
          />

          {/* Start Button */}
          <Button
            variant="primary"
            size="lg"
            onClick={onStartCall}
            className="px-10 py-4 text-lg font-semibold rounded-full bg-white text-black shadow-lg hover:bg-neutral-200 transition"
          >
            {startButtonText}
          </Button>
        </section>
      </div>
    );
  }
);

WelcomeView.displayName = "WelcomeView";
