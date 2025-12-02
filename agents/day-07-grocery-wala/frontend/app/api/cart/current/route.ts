import { NextRequest, NextResponse } from 'next/server';
import fs from 'fs';
import path from 'path';

export async function GET(req: NextRequest) {
  try {
    // Path to current_cart.json in backend orders directory
    const cartPath = path.join(process.cwd(), '..', 'backend', 'src', 'orders', 'current_cart.json');
    
    console.log('Cart API - Looking for cart at:', cartPath);
    console.log('Cart API - File exists:', fs.existsSync(cartPath));
    
    // Check if cart file exists
    if (!fs.existsSync(cartPath)) {
      console.log('Cart API - File not found, returning empty cart');
      const emptyCart = { items: [], total: 0, item_count: 0 };
      
      // Try to create the file
      try {
        const ordersDir = path.join(process.cwd(), '..', 'backend', 'src', 'orders');
        if (!fs.existsSync(ordersDir)) {
          fs.mkdirSync(ordersDir, { recursive: true });
        }
        fs.writeFileSync(cartPath, JSON.stringify(emptyCart, null, 2));
        console.log('Cart API - Created empty cart file');
      } catch (createError) {
        console.error('Cart API - Could not create cart file:', createError);
      }
      
      return NextResponse.json(emptyCart);
    }

    // Read the current cart
    const cartData = JSON.parse(fs.readFileSync(cartPath, 'utf-8'));
    console.log('Cart API - Returning cart data:', cartData);

    // Return cart data
    return NextResponse.json(cartData);
  } catch (error) {
    console.error('Cart API error:', error);
    return NextResponse.json({ items: [], total: 0, item_count: 0 });
  }
}
