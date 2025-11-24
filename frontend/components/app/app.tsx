'use client';

import { RoomAudioRenderer, StartAudio } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionProvider } from '@/components/app/session-provider';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';
import Aurora from "@/components/ui/Aurora";

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <SessionProvider appConfig={appConfig}>
      <div className="relative w-full h-svh overflow-hidden">
        <Aurora
          colorStops={["#7CFF67", "#B19EEF", "#5227FF"]}
          blend={0.45}
          amplitude={1.0}
          speed={0.7}
        />
        <main className="absolute inset-0 grid h-full grid-cols-1 place-content-center">
          <ViewController />
        </main>
      </div>
      <StartAudio label="Enable Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
