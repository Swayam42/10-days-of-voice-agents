'use client';

import React, { useEffect, useState } from 'react';
import { useChatMessages } from '@/hooks/useChatMessages';
import './cart-display.css';

interface CartItem {
  name: string;
  quantity: number;
  price: number;
  unit: string;
}

export const CartDisplay = () => {
  const messages = useChatMessages();
  const [cartItems, setCartItems] = useState<CartItem[]>([]);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    // Parse cart information from agent messages
    const latestMessages = messages.slice(-10); // Check last 10 messages
    
    latestMessages.forEach((msg) => {
      if (!msg.message) return;
      
      const text = msg.message.toLowerCase();
      
      // Detect "your cart:" message for full cart summary
      if (text.includes('your cart:')) {
        parseCartSummary(msg.message);
      }
      // Detect added items
      else if (text.includes('added') && text.includes('to your cart')) {
        parseAddedItem(msg.message);
      }
      // Detect removed items
      else if (text.includes('removed') && text.includes('from cart')) {
        parseRemovedItem(msg.message);
      }
      // Detect cart cleared
      else if (text.includes('cart cleared')) {
        setCartItems([]);
        setTotal(0);
      }
    });
  }, [messages]);

  const parseCartSummary = (message: string) => {
    // Extract items from cart summary message
    // Example: "Your cart: 2x Basmati Rice (1kg) - ₹360, 1x Milk (500ml) - ₹32\n\nTotal: ₹392"
    
    const lines = message.split('\n');
    const items: CartItem[] = [];
    let totalAmount = 0;

    lines.forEach((line) => {
      // Match pattern: "2x Basmati Rice (1kg) - ₹360"
      const itemMatch = line.match(/(\d+)x\s+(.+?)\s+\((.+?)\)\s+-\s+₹(\d+)/);
      if (itemMatch) {
        const [, qty, name, unit, price] = itemMatch;
        items.push({
          name: name.trim(),
          quantity: parseInt(qty),
          price: parseInt(price) / parseInt(qty), // Price per unit
          unit: unit.trim(),
        });
      }

      // Match total: "Total: ₹392"
      const totalMatch = line.match(/Total:\s+₹(\d+)/);
      if (totalMatch) {
        totalAmount = parseInt(totalMatch[1]);
      }
    });

    if (items.length > 0) {
      setCartItems(items);
      setTotal(totalAmount);
    }
  };

  const parseAddedItem = (message: string) => {
    // Example: "Added 2 Basmati Rice (1kg) to your cart. Total now: 2. Price: ₹180 each."
    const match = message.match(/Added\s+(\d+)\s+(.+?)\s+\((.+?)\).*Price:\s+₹(\d+)/i);
    
    if (match) {
      const [, qty, name, unit, price] = match;
      const newItem: CartItem = {
        name: name.trim(),
        quantity: parseInt(qty),
        price: parseInt(price),
        unit: unit.trim(),
      };

      setCartItems((prev) => {
        // Check if item already exists
        const existingIndex = prev.findIndex((item) => item.name === newItem.name);
        if (existingIndex >= 0) {
          const updated = [...prev];
          updated[existingIndex] = newItem;
          return updated;
        }
        return [...prev, newItem];
      });

      // Recalculate total
      setTotal((prev) => prev + newItem.quantity * newItem.price);
    }
  };

  const parseRemovedItem = (message: string) => {
    // Example: "Removed Fresh Paneer from cart"
    const match = message.match(/Removed\s+(.+?)\s+from cart/i);
    
    if (match) {
      const itemName = match[1].trim();
      setCartItems((prev) => {
        const item = prev.find((i) => i.name.includes(itemName) || itemName.includes(i.name));
        if (item) {
          setTotal((t) => t - item.quantity * item.price);
          return prev.filter((i) => i !== item);
        }
        return prev;
      });
    }
  };

  if (cartItems.length === 0) {
    return (
      <div className="cart-display cart-empty">
        <div className="cart-header">
          <span className="cart-icon">🛒</span>
          <span className="cart-title">Your Cart</span>
        </div>
        <p className="cart-empty-text">Khali hai! Start adding items...</p>
      </div>
    );
  }

  return (
    <div className="cart-display">
      <div className="cart-header">
        <span className="cart-icon">🛒</span>
        <span className="cart-title">Your Cart</span>
        <span className="cart-badge">{cartItems.reduce((sum, item) => sum + item.quantity, 0)}</span>
      </div>

      <div className="cart-items">
        {cartItems.map((item, index) => (
          <div key={index} className="cart-item">
            <div className="cart-item-info">
              <span className="cart-item-name">{item.name}</span>
              <span className="cart-item-unit">{item.unit}</span>
            </div>
            <div className="cart-item-details">
              <span className="cart-item-qty">{item.quantity}x</span>
              <span className="cart-item-price">₹{item.quantity * item.price}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="cart-total">
        <span className="cart-total-label">Total</span>
        <span className="cart-total-amount">₹{total}</span>
      </div>

      <div className="cart-footer">
        <span className="cart-footer-text">Say "place my order" to checkout</span>
      </div>
    </div>
  );
};
