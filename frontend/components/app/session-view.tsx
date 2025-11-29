'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';

const MotionBottom = motion.create('div');

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';
const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden' as const,
  animate: 'visible' as const,
  exit: 'hidden' as const,
  transition: {
    duration: 0.3,
    delay: 0.2,
    ease: [0.22, 1, 0.36, 1] as [number, number, number, number],
  },
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}
interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      // Smooth scroll to bottom whenever new messages arrive
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages]);

  const messageCount = messages.length;
  const phase: 'landing' | 'search' | 'burning' =
    messageCount < 5 ? 'landing' : messageCount < 11 ? 'search' : 'burning';

  return (
    <section
      className={cn('relative h-full w-full overflow-hidden bg-[#0a0506]')}
      data-phase={phase}
      {...props}
    >
      {/* Dynamic gradient background based on phase */}
      <div className="absolute inset-0">
        <div className={cn(
          "absolute inset-0 transition-all duration-1000",
          phase === 'landing' && "bg-gradient-to-br from-[#1a0a0f] via-[#2d1410] to-[#0a0506]",
          phase === 'search' && "bg-gradient-to-br from-[#0f1a0a] via-[#1a2d14] to-[#0a0506]",
          phase === 'burning' && "bg-gradient-to-br from-[#1a0a00] via-[#2d1400] to-[#0a0506]"
        )} />
        {/* Subtle pattern overlay */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYgMi42ODYgNiA2cy0yLjY4NiA2LTYgNi02LTIuNjg2LTYtNiAyLjY4Ni02IDYtNnoiIHN0cm9rZT0icmdiYSgyNTUsIDIxNSwgMCwgMC4wMykiLz48L2c+PC9zdmc+')] opacity-20" />
      </div>

      {/* Ambient glowing orbs */}
      <div className={cn(
        "absolute w-96 h-96 rounded-full blur-[120px] opacity-20 transition-all duration-1000",
        phase === 'landing' && "top-1/4 left-1/4 bg-[#d4751a]",
        phase === 'search' && "top-1/3 left-1/3 bg-[#c9a961]",
        phase === 'burning' && "top-1/4 left-1/4 bg-[#ff6b35]"
      )} />

      {/* Top header - sleek gaming HUD */}
      <header className="fixed inset-x-0 top-0 z-30 flex items-start justify-center px-4 pt-4">
        <div className="flex w-full max-w-5xl items-center justify-between gap-4 rounded-2xl border border-[#d4751a]/30 bg-[#0a0506]/95 px-6 py-3 backdrop-blur-xl shadow-[0_8px_32px_rgba(212,117,26,0.15)]">
          <div className="flex items-center gap-3">
            <div className="text-2xl">ॐ</div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-[#ffd700] tracking-wider">
                RAMAYAN
              </span>
              <span className="text-xs text-[#f5e6d3]/60">
                Sundara Kanda
              </span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-[#00ff88] animate-pulse" />
            <span className="text-xs text-[#f5e6d3]/70">LIVE</span>
          </div>
        </div>
      </header>

      {/* Chat Transcript - Gaming overlay style with instant rendering */}
      <div
        className={cn(
          'pointer-events-none fixed inset-0 grid grid-cols-1 grid-rows-1 transition-all duration-200',
          chatOpen && 'bg-[#0a0506]/60 backdrop-blur-md'
        )}
      >
        <ScrollArea ref={scrollAreaRef} className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[180px]">
          <ChatTranscript
            hidden={!chatOpen}
            messages={messages}
            className="mx-auto max-w-2xl space-y-2 transition-opacity duration-150 ease-out will-change-contents"
          />
        </ScrollArea>
      </div>

      {/* Center: Tiles / assistant only */}
      <div className="pointer-events-none relative z-10 mx-auto flex h-full max-w-4xl flex-col px-4 pb-32 pt-24 md:px-6 md:pb-40">
        <div className="relative flex-1">
          <TileLayout chatOpen={chatOpen} />
        </div>
      </div>

      {/* Bottom */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}
        <div className="relative mx-auto max-w-2xl pb-3 md:pb-12">
          <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
        </div>
      </MotionBottom>
    </section>
  );
};
