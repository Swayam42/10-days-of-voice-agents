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
  companyName: 'LiveKit',
  pageTitle: 'Kruti Coffee AI Barista',
  pageDescription: 'Order your favorite Kruti Coffee using our AI Voice Barista - A natural voice ordering experience',


  supportsChatInput: true,
  supportsVideoInput: false,
  supportsScreenShare: false,
  isPreConnectBufferEnabled: true,

  logo: '/kruti_logo.png',
  accent: '#6B4423',
  logoDark: '/kruti_logo.png',
  accentDark: '#8B6F47',
  startButtonText: 'Place Your Order',

  // for LiveKit Cloud Sandbox
  sandboxId: undefined,
  agentName: undefined,
};
