'use client';

import React, { useEffect, useRef, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'motion/react';
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
    delay: 0.5,
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
        'pointer-events-none h-4',
        top && 'bg-black/5',
        bottom && 'bg-black/5',
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
  const [showGiftBox, setShowGiftBox] = useState(false);
  const [currentRound, setCurrentRound] = useState(0);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  // Track current round from agent messages
  const lastAgentMessage = useMemo(() => {
    const agentMessages = messages.filter(msg => !msg.from?.isLocal);
    return agentMessages.at(-1)?.message || '';
  }, [messages]);

  useEffect(() => {
    const sceneMatch = lastAgentMessage.match(/scene (\d+)/i);
    const roundMatch = lastAgentMessage.match(/round (\d+)/i);
    
    if (sceneMatch) {
      setCurrentRound(parseInt(sceneMatch[1]));
    } else if (roundMatch) {
      setCurrentRound(parseInt(roundMatch[1]));
    }
  }, [lastAgentMessage]);

  useEffect(() => {
    const lastMessage = messages.at(-1);
    const lastMessageIsLocal = lastMessage?.from?.isLocal === true;

    if (scrollAreaRef.current && lastMessageIsLocal) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }

    // Check if game ended and show gift box - trigger on any mention of gift
    const lowerMessage = lastAgentMessage.toLowerCase();
    if (lastAgentMessage && !showGiftBox &&
        (lowerMessage.includes('check your screen') ||
         lowerMessage.includes('gift box') ||
         lowerMessage.includes('special gift'))) {
      console.log('Gift box trigger detected:', lastAgentMessage);
      setTimeout(() => setShowGiftBox(true), 2000);
    }
  }, [messages, lastAgentMessage, showGiftBox]);

  return (
    <section className="bg-background relative z-10 h-full w-full overflow-hidden" {...props}>
      {/* Chat Transcript */}
      <div
        className={cn(
          'fixed inset-0 grid grid-cols-1 grid-rows-1',
          !chatOpen && 'pointer-events-none'
        )}
      >
        <Fade top className="absolute inset-x-4 top-0 h-40" />
        <ScrollArea ref={scrollAreaRef} className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[180px]">
          <ChatTranscript
            hidden={!chatOpen}
            messages={messages}
            className="mx-auto max-w-2xl space-y-3 transition-opacity duration-300 ease-out"
          />
        </ScrollArea>
      </div>

      {/* Tile Layout */}
      <TileLayout chatOpen={chatOpen} />

      {/* Round Indicator */}
      <AnimatePresence>
        {currentRound > 0 && currentRound <= 3 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.8, y: -20 }}
            transition={{ duration: 0.4 }}
            className="fixed top-6 right-6 z-50"
          >
            <motion.div
              animate={{ 
                scale: [1, 1.05, 1],
              }}
              transition={{ 
                duration: 2,
                repeat: Infinity,
                ease: "easeInOut"
              }}
              className="bg-black/80 backdrop-blur-sm border-2 border-white/20 rounded-2xl px-6 py-4 shadow-2xl"
            >
              <div className="flex items-center gap-3">
                <div className="text-4xl">🎭</div>
                <div className="flex flex-col">
                  <span className="text-white/60 text-xs font-medium uppercase tracking-wider">Current</span>
                  <span className="text-white text-2xl font-bold tracking-tight">Round {currentRound}</span>
                </div>
              </div>
              
              {/* Progress Dots */}
              <div className="flex gap-2 mt-3 justify-center">
                {[1, 2, 3].map((round) => (
                  <motion.div
                    key={round}
                    initial={{ scale: 0 }}
                    animate={{ 
                      scale: round <= currentRound ? 1 : 0.7,
                      opacity: round <= currentRound ? 1 : 0.3
                    }}
                    transition={{ duration: 0.3, delay: round * 0.1 }}
                    className={cn(
                      "w-2 h-2 rounded-full",
                      round <= currentRound ? "bg-white" : "bg-white/30"
                    )}
                  />
                ))}
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Gift Box Surprise - Minimal Version */}
      <AnimatePresence>
        {showGiftBox && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 backdrop-blur-md"
            onClick={() => window.open('https://www.youtube.com/watch?v=dQw4w9WgXcQ', '_blank')}
          >
            {/* Minimal Confetti */}
            {[...Array(8)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ 
                  x: '50vw', 
                  y: '50vh', 
                  opacity: 1,
                  scale: 0 
                }}
                animate={{ 
                  x: `${Math.random() * 100}vw`,
                  y: `${Math.random() * 100}vh`,
                  opacity: [1, 1, 0],
                  scale: [0, 1, 0.5],
                  rotate: Math.random() * 360
                }}
                transition={{ 
                  duration: 2 + Math.random() * 2,
                  ease: "easeOut",
                  delay: Math.random() * 0.5
                }}
                className="absolute w-3 h-3 rounded-full"
                style={{
                  backgroundColor: ['#ff6b6b', '#4ecdc4', '#ffe66d'][i % 3]
                }}
              />
            ))}

            {/* Gift Box Container - Simplified */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ 
                duration: 0.6, 
                type: "spring",
                bounce: 0.5
              }}
              className="cursor-pointer relative z-10"
            >
              <motion.div
                animate={{ 
                  y: [0, -10, 0],
                }}
                transition={{ 
                  duration: 2,
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
                className="relative flex flex-col items-center"
              >
                {/* Simple Gift Box */}
                <div className="relative w-48 h-48 bg-red-600 rounded-3xl shadow-2xl border-4 border-yellow-400">
                  {/* Shine effect */}
                  <div className="absolute inset-0 bg-white/10 rounded-3xl"></div>
                  
                  {/* Ribbon Vertical */}
                  <div className="absolute inset-x-0 top-0 bottom-0 w-10 bg-yellow-400 left-1/2 -translate-x-1/2"></div>
                  {/* Ribbon Horizontal */}
                  <div className="absolute inset-y-0 left-0 right-0 h-10 bg-yellow-400 top-1/2 -translate-y-1/2"></div>
                  
                  {/* Bow */}
                  <div className="absolute -top-6 left-1/2 -translate-x-1/2">
                    <div className="w-12 h-12 bg-yellow-400 rounded-full shadow-xl border-2 border-yellow-300"></div>
                  </div>
                  
                  {/* Sparkles */}
                  <motion.div
                    animate={{ 
                      scale: [1, 1.3, 1],
                      opacity: [0.8, 1, 0.8],
                      rotate: [0, 180, 360]
                    }}
                    transition={{ 
                      duration: 3,
                      repeat: Infinity,
                    }}
                    className="absolute -top-3 -left-3 text-4xl"
                  >
                    ✨
                  </motion.div>
                  <motion.div
                    animate={{ 
                      scale: [1, 1.3, 1],
                      opacity: [0.8, 1, 0.8],
                      rotate: [0, -180, -360]
                    }}
                    transition={{ 
                      duration: 3,
                      repeat: Infinity,
                      delay: 0.5
                    }}
                    className="absolute -top-3 -right-3 text-4xl"
                  >
                    ✨
                  </motion.div>
                </div>
                
                {/* Text */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.5 }}
                  className="text-center mt-8"
                >
                  <p className="text-white text-4xl font-bold drop-shadow-2xl mb-3">
                    🎉 Congratulations! 🎉
                  </p>
                  <p className="text-yellow-400 text-xl font-semibold drop-shadow-lg">
                    Click to claim your prize!
                  </p>
                </motion.div>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Bottom */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={messages} className="pb-4" />
        )}
        <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
        </div>
      </MotionBottom>
    </section>
  );
};
