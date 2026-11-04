from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
import uuid
import json
import traceback
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'christie-frost-beauty-secret-2026'

# ============================================
# PRODUCTS
# ============================================
PRODUCTS = {
    'glow_serum': {
        'id': 'glow_serum',
        'name': 'Glow Repair Serum',
        'price': 34.99,
        'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop&q=80',
        'category': 'Serums',
        'description': 'Powerful vitamin C serum for radiant, glowing skin.',
        'rating': 4.8,
        'reviews': 234,
        'badge': 'Best Seller',
        'stock': 45
    },
    'hydrating_cream': {
        'id': 'hydrating_cream',
        'name': 'Hydrating Moisture Cream',
        'price': 28.99,
        'image': 'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=400&fit=crop&q=80',
        'category': 'Moisturizers',
        'description': 'Deep hydration cream with hyaluronic acid.',
        'rating': 4.6,
        'reviews': 189,
        'badge': 'New',
        'stock': 60
    },
    'sunscreen_spf': {
        'id': 'sunscreen_spf',
        'name': 'SPF 50 Sunscreen',
        'price': 24.99,
        'image': 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?w=400&h=400&fit=crop&q=80',
        'category': 'Sun Care',
        'description': 'Lightweight, non-greasy sunscreen with SPF 50.',
        'rating': 4.5,
        'reviews': 156,
        'badge': '',
        'stock': 80
    },
    'face_mask': {
        'id': 'face_mask',
        'name': 'Detox Clay Mask',
        'price': 19.99,
        'image': 'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400&h=400&fit=crop&q=80',
        'category': 'Masks',
        'description': 'Purifying clay mask that draws out impurities.',
        'rating': 4.4,
        'reviews': 98,
        'badge': '',
        'stock': 55
    },
    'cleansing_balm': {
        'id': 'cleansing_balm',
        'name': 'Cleansing Balm',
        'price': 22.99,
        'image': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop&q=80',
        'category': 'Cleansers',
        'description': 'Gentle cleansing balm that melts away makeup.',
        'rating': 4.3,
        'reviews': 78,
        'badge': '',
        'stock': 70
    },
    'toner': {
        'id': 'toner',
        'name': 'Hydrating Facial Toner',
        'price': 18.99,
        'image': 'https://images.unsplash.com/photo-1586611292717-f828b167408c?w=400&h=400&fit=crop&q=80',
        'category': 'Toners',
        'description': 'Alcohol-free toner that balances and hydrates.',
        'rating': 4.2,
        'reviews': 67,
        'badge': '',
        'stock': 90
    },
    'peptide_cream': {
        'id': 'peptide_cream',
        'name': 'Peptide Firming Cream',
        'price': 38.99,
        'image': 'https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400&h=400&fit=crop&q=80',
        'category': 'Moisturizers',
        'description': 'Advanced peptide cream that firms and lifts skin.',
        'rating': 4.8,
        'reviews': 167,
        'badge': 'New',
        'stock': 35
    },
    'rose_toner': {
        'id': 'rose_toner',
        'name': 'Rose Hydrating Toner',
        'price': 21.99,
        'image': 'https://images.unsplash.com/photo-1586611292717-f828b167408c?w=400&h=400&fit=crop&q=80',
        'category': 'Toners',
        'description': 'Gentle rose-infused toner that hydrates and soothes.',
        'rating': 4.6,
        'reviews': 145,
        'badge': 'Trending',
        'stock': 50
    }
}

# ============================================
# BUNDLES
# ============================================
BUNDLES = {
    'skincare_starter': {
        'id': 'skincare_starter',
        'name': 'Skincare Starter Bundle',
        'price': 49.99,
        'products': ['cleansing_balm', 'toner', 'hydrating_cream'],
        'savings': 20.98,
        'popular': True,
        'image': 'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop&q=80'
    },
    'glow_bundle': {
        'id': 'glow_bundle',
        'name': 'Glow Getter Bundle',
        'price': 69.99,
        'products': ['glow_serum', 'rose_toner', 'sunscreen_spf'],
        'savings': 28.98,
        'popular': True,
        'image': 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?w=400&h=400&fit=crop&q=80'
    },
    'night_renewal': {
        'id': 'night_renewal',
        'name': 'Night Renewal Bundle',
        'price': 89.99,
        'products': ['cleansing_balm', 'peptide_cream', 'hydrating_cream'],
        'savings': 41.97,
        'popular': False,
        'image': 'https://images.unsplash.com/photo-1612817288484-6f916006741a?w=400&h=400&fit=crop&q=80'
    }
}

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_cart():
    """Get cart and convert from old list format to dict if needed"""
    cart = session.get('cart', {})

    if isinstance(cart, list):
        new_cart = {}
        for item_id in cart:
            new_cart[item_id] = new_cart.get(item_id, 0) + 1
        session['cart'] = new_cart
        session.modified = True
        return new_cart

    if not isinstance(cart, dict):
        session['cart'] = {}
        session.modified = True
        return {}

    return cart


def build_cart_summary():
    """Build cart_items, subtotal, total_items, shipping, total for rendering."""
    cart = get_cart()
    cart_items = []
    subtotal = 0
    total_items = 0

    for item_id, quantity in cart.items():
        if quantity <= 0:
            continue

        if item_id in PRODUCTS:
            product = PRODUCTS[item_id]
            item_total = product['price'] * quantity
            cart_items.append({
                'id': item_id,
                'name': product['name'],
                'price': product['price'],
                'image': product['image'],
                'type': 'product',
                'quantity': quantity,
                'item_total': round(item_total, 2),
                'stock': product['stock']
            })
            subtotal += item_total
            total_items += quantity

        elif item_id in BUNDLES:
            bundle = BUNDLES[item_id]
            item_total = bundle['price'] * quantity
            cart_items.append({
                'id': item_id,
                'name': bundle['name'],
                'price': bundle['price'],
                'image': bundle['image'],
                'type': 'bundle',
                'quantity': quantity,
                'item_total': round(item_total, 2),
                'products': bundle['products']
            })
            subtotal += item_total
            total_items += quantity

    shipping = 0 if subtotal >= 35 else 5.99
    total = subtotal + shipping

    return {
        'cart_items': cart_items,
        'subtotal': round(subtotal, 2),
        'shipping': round(shipping, 2),
        'total': round(total, 2),
        'total_items': total_items
    }


# ============================================
# ROUTES
# ============================================

@app.route('/')
def index():
    try:
        best_sellers = []
        new_arrivals = []
        trending = []

        for product in PRODUCTS.values():
            if product.get('badge') == 'Best Seller':
                best_sellers.append(product)
            elif product.get('badge') == 'New':
                new_arrivals.append(product)
            elif product.get('badge') == 'Trending':
                trending.append(product)

        # Build live cart summary so the shop header can show cart totals safely
        summary = build_cart_summary()

        return render_template('shop.html',
            products=PRODUCTS,
            bundles=BUNDLES,
            best_sellers=best_sellers,
            new_arrivals=new_arrivals,
            trending=trending,
            all_products=PRODUCTS,
            # Safe defaults for shop header/cart badge (prevents 'total' undefined error)
            cart_items=summary['cart_items'],
            subtotal=summary['subtotal'],
            shipping=summary['shipping'],
            total=summary['total'],
            total_items=summary['total_items']
        )
    except Exception as e:
        traceback.print_exc()
        return f"<h1>Error loading shop</h1><pre>{traceback.format_exc()}</pre>", 500


# ============================================
# CART
# ============================================

@app.route('/cart')
def cart():
    try:
        summary = build_cart_summary()
        return render_template('cart.html', **summary)
    except Exception as e:
        traceback.print_exc()
        return f"<h1>Error loading cart</h1><pre>{traceback.format_exc()}</pre>", 500


@app.route('/add-to-cart/<item_id>', methods=['POST'])
def add_to_cart(item_id):
    try:
        cart = get_cart()

        if item_id in PRODUCTS or item_id in BUNDLES:
            if item_id in PRODUCTS:
                current_qty = cart.get(item_id, 0)
                if current_qty >= PRODUCTS[item_id]['stock']:
                    return jsonify({
                        'success': False,
                        'message': 'Not enough stock available!'
                    })

            cart[item_id] = cart.get(item_id, 0) + 1
            session['cart'] = cart
            session.modified = True

            total_items = sum(cart.values())
            return jsonify({
                'success': True,
                'message': 'Added to bag!',
                'count': total_items,
                'quantity': cart[item_id]
            })

        return jsonify({'success': False, 'message': 'Product not found'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/remove-from-cart/<item_id>', methods=['POST'])
def remove_from_cart(item_id):
    try:
        cart = get_cart()
        if item_id in cart:
            del cart[item_id]
            session['cart'] = cart
            session.modified = True
            total_items = sum(cart.values())
            return jsonify({
                'success': True,
                'message': 'Removed from bag!',
                'count': total_items
            })
        return jsonify({'success': False, 'message': 'Item not in bag'})
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/update-cart/<item_id>/<action>', methods=['POST'])
def update_cart(item_id, action):
    try:
        cart = get_cart()

        if action == 'increase':
            if item_id in PRODUCTS:
                current = cart.get(item_id, 0)
                if current >= PRODUCTS[item_id]['stock']:
                    return jsonify({
                        'success': False,
                        'message': 'Not enough stock available!'
                    })
            cart[item_id] = cart.get(item_id, 0) + 1

        elif action == 'decrease':
            if item_id in cart:
                if cart[item_id] <= 1:
                    del cart[item_id]
                else:
                    cart[item_id] -= 1
            else:
                return jsonify({'success': False, 'message': 'Item not in cart'})

        elif action == 'remove':
            if item_id in cart:
                del cart[item_id]
            else:
                return jsonify({'success': False, 'message': 'Item not in cart'})
        else:
            return jsonify({'success': False, 'message': 'Invalid action'})

        session['cart'] = cart
        session.modified = True

        subtotal = 0
        for iid, qty in cart.items():
            if iid in PRODUCTS:
                subtotal += PRODUCTS[iid]['price'] * qty
            elif iid in BUNDLES:
                subtotal += BUNDLES[iid]['price'] * qty

        shipping = 0 if subtotal >= 35 else 5.99
        total = subtotal + shipping

        item_price = 0
        if item_id in PRODUCTS:
            item_price = PRODUCTS[item_id]['price']
        elif item_id in BUNDLES:
            item_price = BUNDLES[item_id]['price']

        return jsonify({
            'success': True,
            'quantity': cart.get(item_id, 0),
            'subtotal': round(subtotal, 2),
            'shipping': round(shipping, 2),
            'total': round(total, 2),
            'total_items': sum(cart.values()),
            'item_total': round(item_price * cart.get(item_id, 0), 2)
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# CHECKOUT — with built-in diagnostics
# ============================================

@app.route('/checkout')
def checkout():
    try:
        cart = get_cart()
        if not cart:
            return redirect(url_for('index'))

        summary = build_cart_summary()

        # Try rendering the template; if it fails, show the exact error
        try:
            return render_template('checkout.html', **summary)
        except Exception as template_error:
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Checkout Template Error</title>
            <script src="https://cdn.tailwindcss.com"></script></head>
            <body class="p-8 bg-gray-50">
                <h1 class="text-3xl font-bold text-red-600 mb-4">❌ Checkout Template Error</h1>
                <div class="bg-white p-6 rounded-xl shadow mb-6">
                    <p class="font-semibold mb-2">Error message:</p>
                    <pre class="bg-red-50 p-4 rounded text-red-800 overflow-auto">{template_error}</pre>
                </div>
                <div class="bg-white p-6 rounded-xl shadow mb-6">
                    <p class="font-semibold mb-2">Full traceback:</p>
                    <pre class="bg-gray-100 p-4 rounded text-xs overflow-auto">{traceback.format_exc()}</pre>
                </div>
                <div class="bg-green-50 p-6 rounded-xl">
                    <p class="font-semibold mb-2 text-green-800">✅ Cart data is OK:</p>
                    <p>Items: {len(summary['cart_items'])}</p>
                    <p>Subtotal: ${summary['subtotal']}</p>
                    <p>Shipping: ${summary['shipping']}</p>
                    <p>Total: ${summary['total']}</p>
                </div>
                <p class="mt-6"><a href="/cart" class="text-blue-600 underline">← Back to Cart</a></p>
            </body>
            </html>
            """
            return error_html, 500

    except Exception as route_error:
        traceback.print_exc()
        return f"""
        <!DOCTYPE html>
        <html><head><title>Checkout Route Error</title>
        <script src="https://cdn.tailwindcss.com"></script></head>
        <body class="p-8 bg-gray-50">
            <h1 class="text-3xl font-bold text-red-600 mb-4">❌ Checkout Route Error</h1>
            <pre class="bg-red-50 p-4 rounded text-red-800 overflow-auto">{traceback.format_exc()}</pre>
            <p class="mt-4"><a href="/cart" class="text-blue-600 underline">← Back to Cart</a></p>
        </body></html>
        """, 500


@app.route('/place-order', methods=['POST'])
def place_order():
    try:
        cart = get_cart()
        if not cart:
            return jsonify({'success': False, 'message': 'Cart is empty'})

        subtotal = 0
        for item_id, quantity in cart.items():
            if item_id in PRODUCTS:
                subtotal += PRODUCTS[item_id]['price'] * quantity
            elif item_id in BUNDLES:
                subtotal += BUNDLES[item_id]['price'] * quantity

        shipping = 0 if subtotal >= 35 else 5.99
        total = subtotal + shipping

        order_id = f"CF-{uuid.uuid4().hex[:8].upper()}"

        session['cart'] = {}
        session.modified = True

        return jsonify({
            'success': True,
            'order_id': order_id,
            'total': round(total, 2),
            'message': 'Order placed successfully!'
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/order-confirmation/<order_id>')
def order_confirmation(order_id):
    return render_template('confirmation.html', order_id=order_id)


@app.route('/clear-cart', methods=['POST'])
def clear_cart():
    session['cart'] = {}
    session.modified = True
    return jsonify({'success': True, 'message': 'Cart cleared'})


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
