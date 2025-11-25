"use client";
import { forwardRef } from "react";
import { Button } from '@/components/livekit/button';
import Galaxy from '@/components/ui/Galaxy';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="relative flex min-h-screen items-center justify-center p-6">
      {/* Galaxy Background */}
      <div className="absolute inset-0 z-0">
        <Galaxy 
          mouseRepulsion={false}
          mouseInteraction={true}
          density={0.4}
          glowIntensity={0.2}
          saturation={0}
          hueShift={140}
          transparent={true}
          speed={0.5}
          twinkleIntensity={0.3}
          rotationSpeed={0.1}
        />
      </div>
      
      <section className="relative z-10 flex max-w-2xl flex-col items-center text-center">
        <div className="mb-12 space-y-4">
          <h1 className="text-5xl font-light tracking-tight md:text-6xl">
            AI Active Recall Coach
          </h1>
          <p className="text-muted-foreground mx-auto max-w-md text-base font-light leading-relaxed">
            Master concepts through active recall.
            <br />
            Learn, quiz, and teach back.
          </p>
        </div>
        
        <div className="space-y-3">
          <Button 
            variant="primary" 
            size="lg" 
            onClick={onStartCall} 
            className="w-56 border border-foreground/10 bg-foreground font-bold tracking-wide text-background transition-all hover:bg-foreground/90"
          >
            {startButtonText}
          </Button>
          <p className="text-muted-foreground text-xs font-light">
            Three modes: Learn · Quiz · Teach Back
          </p>
        </div>
      </section>
    </div>
  );
};
