import { forwardRef } from "react";
import { Button } from "@/components/livekit/button";
import Image from "next/image";

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = forwardRef<HTMLDivElement, WelcomeViewProps>(
  ({ startButtonText, onStartCall }, ref) => {
    return (
      <div ref={ref} className="welcome-container">
        {/* LEFT SECTION */}
        <div className="welcome-left">
          <div className="welcome-badge">Concept Demo</div>

          <h1 className="welcome-title">
            KRUTI <br />
            COFFEE <br />
            AI BARISTA
          </h1>

          <p className="welcome-subtitle">
            Day 2 of 10 Days of Voice Agents Challenge by{" "}
            <a
              className="murf-link-embed underline"
              href="https://murf.ai/"
              target="_blank"
              rel="noopener noreferrer"
            >
              Murf AI
            </a>
          </p>
        </div>

        {/* RIGHT SECTION */}
        <div className="welcome-right">
          <div className="welcome-logo-container">
            <Image
              src="/kruti_logo.png"
              alt="Kruti Coffee"
              width={90}
              height={90}
              className="welcome-logo"
            />
          </div>

          <div className="welcome-content">
            <Image
              src="/barista.png"
              alt="Barista"
              width={300}
              height={400}
              className="welcome-barista"
            />

            <Button
              variant="primary"
              size="lg"
              onClick={onStartCall}
              className="welcome-button"
            >
              {startButtonText}
            </Button>
          </div>
        </div>
      </div>
    );
  }
);

WelcomeView.displayName = "WelcomeView";
