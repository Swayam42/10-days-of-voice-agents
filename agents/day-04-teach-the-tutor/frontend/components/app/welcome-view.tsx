"use client";
import { forwardRef } from "react";
import { Button } from '@/components/livekit/button';
import Galaxy from '@/components/ui/Galaxy';
import SpotlightCard from '@/components/ui/SpotlightCard';
import { BookOpenText, Question, Chalkboard } from '@phosphor-icons/react/dist/ssr';

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
      
      <section className="relative z-10 flex w-full max-w-5xl flex-col items-center">
        {/* Header */}
        <div className="mb-12 space-y-4 text-center">
          <h1 className="font-mono text-5xl font-light tracking-tight md:text-6xl">
            AI Active Recall Coach
          </h1>
          <p className="text-muted-foreground mx-auto max-w-md text-base font-light leading-relaxed">
            Master concepts through active recall.
          </p>
        </div>

        {/* Spotlight Cards */}
        <div className="mb-12 grid w-full grid-cols-1 gap-4 md:grid-cols-3 md:gap-6">
          <SpotlightCard className="p-6 border-foreground/10 bg-background/40 backdrop-blur-sm">
            <div className="flex flex-col space-y-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-foreground/10 bg-foreground/5">
                <BookOpenText size={24} weight="duotone" className="text-foreground" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-normal tracking-tight text-foreground">Learn</h3>
                <p className="text-sm font-light leading-relaxed text-muted-foreground">
                  Matthew explains concepts with crystal clarity using vivid analogies and storytelling.
                </p>
              </div>
            </div>
          </SpotlightCard>

          <SpotlightCard className="border-foreground/10 bg-background/40 backdrop-blur-sm">
            <div className="flex flex-col space-y-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-foreground/10 bg-foreground/5">
                <Question size={24} weight="duotone" className="text-foreground" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-normal tracking-tight text-foreground">Quiz</h3>
                <p className="text-sm font-light leading-relaxed text-muted-foreground">
                  Alicia challenges your understanding with thought-provoking questions and adaptive feedback.
                </p>
              </div>
            </div>
          </SpotlightCard>

          <SpotlightCard className="border-foreground/10 bg-background/40 backdrop-blur-sm">
            <div className="flex flex-col space-y-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-sm border border-foreground/10 bg-foreground/5">
                <Chalkboard size={24} weight="duotone" className="text-foreground" />
              </div>
              <div className="space-y-1">
                <h3 className="text-lg font-normal tracking-tight text-foreground">Teach Back</h3>
                <p className="text-sm font-light leading-relaxed text-muted-foreground">
                  Ken learns from you as you explain concepts, revealing deep understanding.
                </p>
              </div>
            </div>
          </SpotlightCard>
        </div>
        
        {/* CTA */}
        <div className="flex flex-col items-center space-y-3">
          <Button 
            variant="primary" 
            size="lg" 
            onClick={onStartCall} 
            className="w-56 border border-foreground/10 bg-foreground font-bold tracking-wide text-background transition-all hover:bg-foreground/90"
          >
            {startButtonText}
          </Button>
          <p className="text-muted-foreground text-xs font-light">
            Choose your learning mode after connecting
          </p>
        </div>
      </section>
    </div>
  );
};
