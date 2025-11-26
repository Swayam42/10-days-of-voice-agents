import { Button } from '@/components/livekit/button';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

const HoneycombCell = ({ delay = 0, size = 80 }: { delay?: number; size?: number }) => (
  <div
    className="honeycomb-float absolute opacity-[0.08]"
    style={{
      animationDelay: `${delay}s`,
      width: `${size}px`,
      height: `${size * 1.15}px`,
    }}
  >
    <svg viewBox="0 0 100 115" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M50 0L93.3 28.75V86.25L50 115L6.7 86.25V28.75L50 0Z"
        stroke="currentColor"
        strokeWidth="2"
        fill="none"
        className="text-primary"
      />
    </svg>
  </div>
);

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="relative min-h-screen overflow-hidden bg-background">
      {/* Animated Honeycomb Background */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <HoneycombCell delay={0} size={120} />
        <div style={{ position: 'absolute', top: '10%', left: '15%' }}>
          <HoneycombCell delay={1} size={100} />
        </div>
        <div style={{ position: 'absolute', top: '5%', right: '20%' }}>
          <HoneycombCell delay={2} size={90} />
        </div>
        <div style={{ position: 'absolute', top: '40%', left: '5%' }}>
          <HoneycombCell delay={0.5} size={110} />
        </div>
        <div style={{ position: 'absolute', top: '60%', right: '10%' }}>
          <HoneycombCell delay={1.5} size={95} />
        </div>
        <div style={{ position: 'absolute', bottom: '15%', left: '25%' }}>
          <HoneycombCell delay={2.5} size={85} />
        </div>
        <div style={{ position: 'absolute', bottom: '20%', right: '30%' }}>
          <HoneycombCell delay={3} size={105} />
        </div>
        <div style={{ position: 'absolute', top: '25%', right: '5%' }}>
          <HoneycombCell delay={1.8} size={75} />
        </div>
      </div>

      {/* Hero Section */}
      <section className="relative flex flex-col items-center justify-center px-6 py-20 text-center">
        <div className="mb-6 inline-block rounded-full border border-primary/20 bg-primary/5 px-5 py-2">
          <span className="text-sm font-semibold text-primary">AI-Powered Sales Assistant</span>
        </div>
        
        <h1 className="mb-6 text-6xl font-bold tracking-tight text-foreground md:text-7xl">
          <span className="bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            XpressBees
          </span>{' '}
          <span className="bg-gradient-to-r from-primary to-primary/70 bg-clip-text text-transparent">
            SDR
          </span>
        </h1>
        
        <p className="mb-10 max-w-2xl text-xl leading-relaxed text-muted-foreground">
          Your intelligent sales development representative. Schedule meetings, qualify leads, 
          and accelerate your sales pipeline with voice-enabled AI.
        </p>
        
        <Button 
          variant="primary" 
          size="lg" 
          onClick={onStartCall} 
          className="group h-14 px-10 text-lg font-semibold shadow-lg shadow-primary/2 transition-all hover:scale-105"
        >
          {startButtonText}
          <svg className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </Button>
      </section>

      {/* Stats Section */}
      <section className="relative border-y border-border/50 bg-gradient-to-b from-background to-muted/30 px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="grid grid-cols-1 gap-12 md:grid-cols-3">
            <div className="group text-center transition-transform hover:scale-105">
              <div className="mb-3 text-5xl font-bold text-primary">24/7</div>
              <div className="text-base font-medium text-foreground">Always Available</div>
              <div className="mt-1 text-sm text-muted-foreground">Round-the-clock support</div>
            </div>
            <div className="group text-center transition-transform hover:scale-105">
              <div className="mb-3 text-5xl font-bold text-primary">100%</div>
              <div className="text-base font-medium text-foreground">Lead Qualification</div>
              <div className="mt-1 text-sm text-muted-foreground">Intelligent screening</div>
            </div>
            <div className="group text-center transition-transform hover:scale-105">
              <div className="mb-3 text-5xl font-bold text-primary">&lt;5min</div>
              <div className="text-base font-medium text-foreground">Response Time</div>
              <div className="mt-1 text-sm text-muted-foreground">Instant engagement</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section className="relative px-6 py-20">
        <div className="mx-auto max-w-6xl">
          <div className="mb-16 text-center">
            <h2 className="mb-4 text-4xl font-bold text-foreground">
              Why Choose XpressBees SDR?
            </h2>
            <p className="mx-auto max-w-2xl text-lg text-muted-foreground">
              Delivering happiness through intelligent automation and seamless logistics
            </p>
          </div>
          
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="group rounded-xl border border-border bg-card p-7 shadow-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/15">
                <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Smart Scheduling</h3>
              <p className="leading-relaxed text-muted-foreground">Automatically book meetings based on calendar availability with intelligent slot suggestions</p>
            </div>

            <div className="group rounded-xl border border-border bg-card p-7 shadow-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/15">
                <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Lead Qualification</h3>
              <p className="leading-relaxed text-muted-foreground">Intelligent conversation flow to qualify prospects and collect essential information</p>
            </div>

            <div className="group rounded-xl border border-border bg-card p-7 shadow-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/15">
                <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Instant Response</h3>
              <p className="leading-relaxed text-muted-foreground">No wait times, immediate engagement with natural voice conversations</p>
            </div>

            <div className="group rounded-xl border border-border bg-card p-7 shadow-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/15">
                <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Sales Analytics</h3>
              <p className="leading-relaxed text-muted-foreground">Track conversations, meeting bookings, and lead quality metrics in real-time</p>
            </div>

            <div className="group rounded-xl border border-border bg-card p-7 shadow-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/15">
                <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Email Integration</h3>
              <p className="leading-relaxed text-muted-foreground">Automatic follow-ups and confirmation emails with calendar invites</p>
            </div>

            <div className="group rounded-xl border border-border bg-card p-7 shadow-sm transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
              <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 transition-colors group-hover:bg-primary/15">
                <svg className="h-6 w-6 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="mb-2 text-xl font-semibold text-foreground">Enterprise Security</h3>
              <p className="leading-relaxed text-muted-foreground">Bank-grade encryption and compliance with GDPR, SOC 2, and HIPAA standards</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
