import { Button } from '@/components/livekit/button';
import './welcome-view.css';

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
    <div ref={ref} className="gw-welcome">
      <div className="gw-container">
        <div className="gw-content">
          <h1 className="gw-brand">GroceryWala</h1>
          <p className="gw-tagline">Voice-powered Indian grocery shopping</p>
          
          <div className="gw-features">
            <div className="gw-feature">
              <h3>Voice Shopping</h3>
              <p>Order naturally by talking</p>
            </div>
            <div className="gw-feature">
              <h3>Recipe Intelligence</h3>
              <p>Get ingredients for any dish</p>
            </div>
            <div className="gw-feature">
              <h3>Easy Payment</h3>
              <p>COD or UPI options</p>
            </div>
            <div className="gw-feature">
              <h3>Quick Delivery</h3>
              <p>Fresh groceries delivered</p>
            </div>
          </div>

          <Button 
            variant="primary" 
            size="lg" 
            onClick={onStartCall} 
            className="gw-cta"
          >
            {startButtonText}
          </Button>
        </div>
      </div>
    </div>
  );
};
