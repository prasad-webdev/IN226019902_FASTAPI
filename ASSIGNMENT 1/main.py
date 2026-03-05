from fastapi import FastAPI

app = FastAPI()


products = [
    {"id": 1, "name": "Wireless Mouse", "price": 999, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 149, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Gaming Chair", "price": 15999, "category": "Furniture", "in_stock": False},
    {"id": 4, "name": "Water Bottle", "price": 499, "category": "Lifestyle", "in_stock": True},

    # Q1: Adding 3 more products

    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]

@app.get("/products")
def get_all_products():
    return {"products": products, "total": len(products)}

# Q2: Category Filter Endpoint

@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):
    result = [p for p in products if p["category"].lower() == category_name.lower()]
    if not result:
        return {"error": "No products found in this category"}
    return {"category": category_name, "products": result, "total": len(result)}

# Q3: Show Only In-Stock Products

@app.get("/products/instock")
def get_instock():
    available = [p for p in products if p["in_stock"]]
    return {"in_stock_products": available, "count": len(available)}

# Q4: Store Info Summary Endpoint

@app.get("/store/summary")
def store_summary():
    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count
    categories = list(set([p["category"] for p in products]))
    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories,
    }

# Q5: Search Products by Name (Case-Insensitive)

@app.get("/products/search/{keyword}")
def search_products(keyword: str):
    results = [
        p for p in products 
        if keyword.lower() in p["name"].lower()
    ]
    if not results:
        return {"message": "No products matched your search"}
    return {"keyword": keyword, "results": results, "total_matches": len(results)}

# BONUS: Cheapest & Most Expensive Product

@app.get("/products/deals")
def get_deals():
    if not products:
        return {"error": "No products available"}
    cheapest = min(products, key=lambda p: p["price"])
    expensive = max(products, key=lambda p: p["price"])
    return {
        "best_deal": cheapest,
        "premium_pick": expensive,
    }