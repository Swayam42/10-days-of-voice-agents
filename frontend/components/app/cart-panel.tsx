'use client';

import { useState, useEffect } from 'react';
import './cart-panel.css';

interface CartItem {
  id: string;
  name: string;
  brand: string;
  price: number;
  unit: string;
  quantity: number;
}

interface CartPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CartPanel({ isOpen, onClose }: CartPanelProps) {
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [totalAmount, setTotalAmount] = useState(0);
  const [itemCount, setItemCount] = useState(0);
  const [lastUpdate, setLastUpdate] = useState<string>('');

  // Fetch cart immediately when panel opens and poll continuously
  useEffect(() => {
    const fetchCart = async () => {
      try {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] Fetching cart data...`);
        
        const response = await fetch('/api/cart/current?t=' + Date.now(), {
          cache: 'no-store',
          headers: {
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
          },
        });
        
        console.log(`[${timestamp}] Cart API response status:`, response.status);
        
        if (response.ok) {
          const data = await response.json();
          console.log(`[${timestamp}] Cart data received:`, data);
          setCartItems(data.items || []);
          setTotalAmount(data.total || 0);
          setItemCount(data.item_count || 0);
          setLastUpdate(timestamp);
        } else {
          console.error(`[${timestamp}] Cart API error:`, response.statusText);
          setCartItems([]);
          setTotalAmount(0);
          setItemCount(0);
        }
      } catch (error) {
        console.error('Cart fetch error:', error);
        setCartItems([]);
        setTotalAmount(0);
        setItemCount(0);
      }
    };

    // Always fetch cart data when panel opens
    if (isOpen) {
      console.log('Cart panel opened - starting polling...');
      fetchCart(); // Immediate fetch
      // Poll every 1 second while panel is open for real-time updates
      const interval = setInterval(fetchCart, 1000);
      return () => {
        console.log('Cart panel closed - stopping polling');
        clearInterval(interval);
      };
    }
  }, [isOpen]);

  return (
    <>
      {/* Overlay */}
      <div 
        className={`cart-overlay ${isOpen ? 'cart-overlay-open' : ''}`}
        onClick={onClose}
      />

      {/* Sliding Panel */}
      <div className={`cart-panel ${isOpen ? 'cart-panel-open' : ''}`}>
        {/* Header */}
        <div className="cart-header">
          <div>
            <h2 className="cart-title">Cart</h2>
            <p className="cart-subtitle">{itemCount} {itemCount === 1 ? 'item' : 'items'}</p>
          </div>
          <button 
            onClick={onClose}
            className="cart-close"
            aria-label="Close cart"
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M15 5L5 15M5 5L15 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
          </button>
        </div>

        {/* Cart Items */}
        <div className="cart-content">
          {cartItems.length === 0 ? (
            <div className="cart-empty">
              <p>Your cart is empty</p>
              <p className="cart-empty-hint">Start adding items by talking to the agent</p>
            </div>
          ) : (
            <div className="cart-items">
              {cartItems.map((item) => (
                <div key={item.id} className="cart-item">
                  <div className="cart-item-details">
                    <h3 className="cart-item-name">{item.name}</h3>
                    <p className="cart-item-meta">
                      {item.brand} • {item.unit}
                    </p>
                  </div>
                  <div className="cart-item-right">
                    <span className="cart-item-qty">×{item.quantity}</span>
                    <span className="cart-item-price">
                      ₹{(item.price * item.quantity).toFixed(0)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer with Total */}
        {cartItems.length > 0 && (
          <div className="cart-footer">
            <div className="cart-total">
              <span className="cart-total-label">Total</span>
              <span className="cart-total-amount">₹{totalAmount.toFixed(0)}</span>
            </div>
            <p className="cart-footer-note">
              Say "place my order" to complete checkout
            </p>
          </div>
        )}

        {/* Polling indicator */}
        {lastUpdate && (
          <div style={{ 
            fontSize: '10px', 
            color: '#666', 
            textAlign: 'center', 
            padding: '8px',
            borderTop: '1px solid #e5e5e5'
          }}>
            Last updated: {lastUpdate}
          </div>
        )}
      </div>
    </>
  );
}
