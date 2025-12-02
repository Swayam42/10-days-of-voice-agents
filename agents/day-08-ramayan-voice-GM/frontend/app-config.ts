export interface AppConfig {
  pageTitle: string;
  pageDescription: string;
  companyName: string;

  supportsChatInput: boolean;
  supportsVideoInput: boolean;
  supportsScreenShare: boolean;
  isPreConnectBufferEnabled: boolean;

  logo: string;
  startButtonText: string;
  accent?: string;
  logoDark?: string;
  accentDark?: string;

  // for LiveKit Cloud Sandbox
  sandboxId?: string;
  agentName?: string;
}

export const APP_CONFIG_DEFAULTS: AppConfig = {
  companyName: 'Ramayan Voice RPG',
  pageTitle: 'Ramayan Voice Game Master - Hanuman\'s Journey to Lanka',
  pageDescription: 'Experience the epic tale of Ramayan as Hanuman. Voice-powered D&D-style adventure through ancient India.',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#FF6B35',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#FFA07A',
  startButtonText: '🕉️ शुरू करें (Start Adventure)',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
