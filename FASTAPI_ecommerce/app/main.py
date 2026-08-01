from fastapi import FastAPI, HTTPException, Query, Path
from services.products import get_all_products

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the FastAPI e-commerce application!"}

'''
@app.get("/products")
def get_products():
    return get_all_products()
'''

@app.get("/products")
def list_products(
    name: str = Query(
        default=None,
        min_length=1,
        max_length=50,
        description="Search by product name (case insensitive)",
    ),
    sort_by_price: bool = Query(default=False, description="Sort products by price"),
    order: str = Query(
        default="asc", description="Sort order when sort_by_price=true (asc,desc)"
    ), 
    limit: int = Query(
            default=10,
            ge=1,
            le=100,
            description="Number of items to return",
    ),
    offset: int = Query(
            default=0,
            ge=0,
            description="Pagination Offset",
    ),
):

    # products = get_all_products()
    products = get_all_products()
    
    if name:
        needle = name.strip().lower()
        products = [
            p for p in products 
            if (
                needle in p.get("name", "").lower()
                or needle in p.get("description", "").lower()
                or needle in p.get("brand", "").lower()
                or needle in p.get("category", "").lower()
                or any(needle in tag.lower() for tag in p.get("tags", []))
            )
        ]
    
    if not products:
        raise HTTPException(
            status_code=404, detail=f"No product found matching name={name}"
        )

    if sort_by_price:
        reverse = order == "desc"
        products = sorted(products, key=lambda p: p.get("price", 0), reverse=reverse)
    
    total = len(products)
    products = products[offset : offset + limit]
    return {"total": total, "limit": limit, "items": products}

@app.get("/products/{product_id}")
def get_product_by_id(
    product_id: str = Path(
        ...,
        min_length=36,
        max_length=36,
        description="UUID of the products",
        example="c47ea2457-c4a9-4bfg-9dd5-6464r0ebe343",
    )
):
    products = get_all_products()
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found!")