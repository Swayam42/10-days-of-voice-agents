'use client';

import { useState } from 'react';
import { Button } from '@/components/livekit/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: (playerName?: string) => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  const [playerName, setPlayerName] = useState('');

  const handleStart = () => {
    onStartCall(playerName.trim() || undefined);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleStart();
    }
  };

  return (
    <div ref={ref}>
      <section className="bg-background flex flex-col items-center justify-center text-center px-4 min-h-screen">
        <div className="max-w-md w-full space-y-8">
          {/* Header */}
          <div className="space-y-3">
            <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-foreground">
              Improv Battle
            </h1>
            <p className="text-muted-foreground text-lg">
              3 scenes. Real feedback.
            </p>
          </div>
          
          {/* How it works */}
          <div className="bg-card border border-border rounded-lg p-5 space-y-3">
            <div className="space-y-3 text-sm text-muted-foreground">
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-foreground/10 flex items-center justify-center font-semibold text-xs">1</span>
                <p className="text-left">You'll get an improv scenario</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-foreground/10 flex items-center justify-center font-semibold text-xs">2</span>
                <p className="text-left">Act it out for 20-30 seconds</p>
              </div>
              <div className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 rounded-full bg-foreground/10 flex items-center justify-center font-semibold text-xs">3</span>
                <p className="text-left">Get feedback from the AI host</p>
              </div>
            </div>
          </div>
          
          {/* Name input and start button */}
          <div className="space-y-4">
            <input
              id="player-name"
              type="text"
              value={playerName}
              onChange={(e) => setPlayerName(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Your name"
              className="w-full px-4 py-3 text-base rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-all"
              maxLength={30}
              autoFocus
            />
            
            <Button 
              variant="primary" 
              size="lg" 
              onClick={handleStart} 
              className="w-full font-semibold text-base h-12 rounded-lg"
            >
              {startButtonText}
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};
