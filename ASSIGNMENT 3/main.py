from fastapi import FastAPI, Query, Response, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ══ PYDANTIC MODELS ═══════════════════════════════════════════════

class OrderRequest(BaseModel):
    customer_name:    str = Field(..., min_length=2, max_length=100)
    product_id:       int = Field(..., gt=0)
    quantity:         int = Field(..., gt=0, le=100)
    delivery_address: str = Field(..., min_length=10)

class NewProduct(BaseModel):
    name:     str  = Field(..., min_length=2, max_length=100)
    price:    int  = Field(..., gt=0)
    category: str  = Field(..., min_length=2)
    in_stock: bool = True

class CustomerFeedback(BaseModel):
    customer_name: str           = Field(..., min_length=2, max_length=100)
    product_id:    int           = Field(..., gt=0)
    rating:        int           = Field(..., ge=1, le=5)
    comment:       Optional[str] = Field(None, max_length=300)

class OrderItem(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity:   int = Field(..., gt=0, le=50)

class BulkOrder(BaseModel):
    company_name:  str             = Field(..., min_length=2)
    contact_email: str             = Field(..., min_length=5)
    items:         List[OrderItem] = Field(..., min_length=1)

# ══ DATA ══════════════════════════════════════════════════════════

products = [
    {'id': 1, 'name': 'Wireless Mouse', 'price':  499, 'category': 'Electronics', 'in_stock': True},
    {'id': 2, 'name': 'Notebook',       'price':   99, 'category': 'Stationery',  'in_stock': True},
    {'id': 3, 'name': 'USB Hub',        'price':  799, 'category': 'Electronics', 'in_stock': False},
    {'id': 4, 'name': 'Pen Set',        'price':   49, 'category': 'Stationery',  'in_stock': True},
]

orders        = []
order_counter = 1
feedback      = []

# ══ HELPER FUNCTIONS ══════════════════════════════════════════════

def find_product(product_id: int):
    for p in products:
        if p['id'] == product_id:
            return p
    return None

def calculate_total(product: dict, quantity: int) -> int:
    return product['price'] * quantity

def filter_products_logic(category=None, min_price=None, max_price=None, in_stock=None):
    result = products
    if category  is not None: result = [p for p in result if p['category'] == category]
    if min_price is not None: result = [p for p in result if p['price'] >= min_price]
    if max_price is not None: result = [p for p in result if p['price'] <= max_price]
    if in_stock  is not None: result = [p for p in result if p['in_stock'] == in_stock]
    return result



# ── Home ──────────────────────────────────────────────────────────

@app.get('/')
def home():
    return {'message': 'Welcome to our E-commerce API'}

# ── GET all products ──────────────────────────────────────────────

@app.get('/products')
def get_all_products():
    return {'products': products, 'total': len(products)}

# ══ ALL FIXED /products/* ROUTES — before /{product_id} ══════════

@app.get('/products/filter')
def filter_products(
    category:  str  = Query(None, description='Electronics or Stationery'),
    min_price: int  = Query(None, description='Minimum price'),
    max_price: int  = Query(None, description='Maximum price'),
    in_stock:  bool = Query(None, description='True = in stock only'),
):
    result = filter_products_logic(category, min_price, max_price, in_stock)
    return {'filtered_products': result, 'count': len(result)}

@app.get('/products/compare')
def compare_products(
    product_id_1: int = Query(..., description='First product ID'),
    product_id_2: int = Query(..., description='Second product ID'),
):
    p1 = find_product(product_id_1)
    p2 = find_product(product_id_2)
    if not p1: return {'error': f'Product {product_id_1} not found'}
    if not p2: return {'error': f'Product {product_id_2} not found'}
    cheaper = p1 if p1['price'] < p2['price'] else p2
    return {
        'product_1':    p1,
        'product_2':    p2,
        'better_value': cheaper['name'],
        'price_diff':   abs(p1['price'] - p2['price']),
    }

@app.get('/products/instock')
def get_instock():
    available = [p for p in products if p['in_stock']]
    return {'in_stock_products': available, 'count': len(available)}

@app.get('/products/deals')
def get_deals():
    return {
        'best_deal':    min(products, key=lambda p: p['price']),
        'premium_pick': max(products, key=lambda p: p['price']),
    }

@app.get('/products/search/{keyword}')
def search_products(keyword: str):
    results = [p for p in products if keyword.lower() in p['name'].lower()]
    if not results:
        return {'message': 'No products matched your search'}
    return {'keyword': keyword, 'results': results, 'total_matches': len(results)}

@app.get('/products/category/{category_name}')
def get_by_category(category_name: str):
    result = [p for p in products if p['category'] == category_name]
    if not result:
        return {'error': 'No products found in this category'}
    return {'category': category_name, 'products': result, 'total': len(result)}

@app.get('/products/summary')
def product_summary():
    in_stock  = [p for p in products if     p['in_stock']]
    out_stock = [p for p in products if not p['in_stock']]
    expensive = max(products, key=lambda p: p['price'])
    cheapest  = min(products, key=lambda p: p['price'])
    return {
        'total_products':     len(products),
        'in_stock_count':     len(in_stock),
        'out_of_stock_count': len(out_stock),
        'most_expensive':     {'name': expensive['name'], 'price': expensive['price']},
        'cheapest':           {'name': cheapest['name'],  'price': cheapest['price']},
        'categories':         list(set(p['category'] for p in products)),
    }

@app.get('/products/audit')
def product_audit():
    in_stock_list  = [p for p in products if     p['in_stock']]
    out_stock_list = [p for p in products if not p['in_stock']]
    priciest       = max(products, key=lambda p: p['price']) if products else None
    return {
        'total_products':     len(products),
        'in_stock_count':     len(in_stock_list),
        'out_of_stock_names': [p['name'] for p in out_stock_list],
        'total_stock_value':  sum(p['price'] * 10 for p in in_stock_list),
        'most_expensive':     {'name': priciest['name'], 'price': priciest['price']} if priciest else None,
    }

@app.get('/store/summary')
def store_summary():
    in_stock_count = len([p for p in products if p['in_stock']])
    categories     = list(set(p['category'] for p in products))
    return {
        'store_name':     'My E-commerce Store',
        'total_products': len(products),
        'in_stock':       in_stock_count,
        'out_of_stock':   len(products) - in_stock_count,
        'categories':     categories,
    }

# ── PUT /products/discount — MUST be before PUT /{product_id} ─────

@app.put('/products/discount')
def bulk_discount(
    category:         str = Query(..., description='Category to discount'),
    discount_percent: int = Query(..., ge=1, le=99, description='Discount % (1–99)'),
):
    updated = []
    for p in products:
        if p['category'] == category:
            p['price'] = int(p['price'] * (1 - discount_percent / 100))
            updated.append(p)
    if not updated:
        return {'message': f'No products found in category: {category}'}
    return {
        'message':          f'{discount_percent}% discount applied to {category}',
        'updated_count':    len(updated),
        'updated_products': updated,
    }

# ══ VARIABLE /products/{product_id} ROUTES — always LAST ══════════

@app.get('/products/{product_id}')
def get_product(product_id: int):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
    return {'product': product}

@app.get('/products/{product_id}/price')
def get_product_price(product_id: int):
    product = find_product(product_id)
    if not product:
        return {'error': 'Product not found'}
    return {'name': product['name'], 'price': product['price']}

@app.post('/products')
def add_product(new_product: NewProduct, response: Response):
    existing_names = [p['name'].lower() for p in products]
    if new_product.name.lower() in existing_names:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {'error': 'Product with this name already exists'}
    next_id = max(p['id'] for p in products) + 1
    product = {
        'id':       next_id,
        'name':     new_product.name,
        'price':    new_product.price,
        'category': new_product.category,
        'in_stock': new_product.in_stock,
    }
    products.append(product)
    response.status_code = status.HTTP_201_CREATED
    return {'message': 'Product added', 'product': product}

@app.put('/products/{product_id}')
def update_product(
    product_id: int,
    response:   Response,
    in_stock:   bool = Query(None, description='Update stock status'),
    price:      int  = Query(None, description='Update price'),
):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    if in_stock is not None: product['in_stock'] = in_stock
    if price    is not None: product['price']    = price
    return {'message': 'Product updated', 'product': product}

@app.delete('/products/{product_id}')
def delete_product(product_id: int, response: Response):
    product = find_product(product_id)
    if not product:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {'error': 'Product not found'}
    products.remove(product)
    return {'message': f"Product '{product['name']}' deleted"}

# ══ ORDERS ════════════════════════════════════════════════════════

@app.post('/orders')
def place_order(order_data: OrderRequest):
    global order_counter
    product = find_product(order_data.product_id)
    if not product:
        return {'error': 'Product not found'}
    if not product['in_stock']:
        return {'error': f"{product['name']} is out of stock"}
    order = {
        'order_id':         order_counter,
        'customer_name':    order_data.customer_name,
        'product':          product['name'],
        'quantity':         order_data.quantity,
        'delivery_address': order_data.delivery_address,
        'total_price':      calculate_total(product, order_data.quantity),
        'status':           'pending',
    }
    orders.append(order)
    order_counter += 1
    return {'message': 'Order placed successfully', 'order': order}

@app.get('/orders')
def get_all_orders():
    return {'orders': orders, 'total_orders': len(orders)}

@app.get('/orders/{order_id}')
def get_order_by_id(order_id: int):
    for order in orders:
        if order['order_id'] == order_id:
            return {'order': order}
    return {'error': 'Order not found'}

@app.patch('/orders/{order_id}/confirm')
def confirm_order(order_id: int):
    for order in orders:
        if order['order_id'] == order_id:
            order['status'] = 'confirmed'
            return {'message': 'Order confirmed', 'order': order}
    return {'error': 'Order not found'}

# ══ FEEDBACK ══════════════════════════════════════════════════════

@app.post('/feedback')
def submit_feedback(fb: CustomerFeedback):
    feedback.append(fb.dict())
    return {
        'message':        'Feedback submitted successfully',
        'feedback':       fb.dict(),
        'total_feedback': len(feedback),
    }

# ══ BULK ORDERS ═══════════════════════════════════════════════════

@app.post('/orders/bulk')
def place_bulk_order(order: BulkOrder):
    confirmed, failed, grand_total = [], [], 0
    for item in order.items:
        product = find_product(item.product_id)
        if not product:
            failed.append({'product_id': item.product_id, 'reason': 'Product not found'})
        elif not product['in_stock']:
            failed.append({'product_id': item.product_id, 'reason': f"{product['name']} is out of stock"})
        else:
            subtotal = product['price'] * item.quantity
            grand_total += subtotal
            confirmed.append({'product': product['name'], 'qty': item.quantity, 'subtotal': subtotal})
    return {
        'company':     order.company_name,
        'confirmed':   confirmed,
        'failed':      failed,
        'grand_total': grand_total,
    }

