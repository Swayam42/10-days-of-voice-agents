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
  companyName: 'XpressBees',
  pageTitle: 'XpressBees SDR - AI Sales Assistant',
  pageDescription: 'Intelligent sales development representative powered by voice AI. Schedule meetings, qualify leads, and accelerate your sales pipeline.',

  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/lk-logo.svg',
  accent: '#FF6B35',
  logoDark: '/lk-logo-dark.svg',
  accentDark: '#FF8557',
  startButtonText: 'Start Conversation',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
