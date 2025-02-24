from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
from utils import get_products, generate_recommendations
import json
import logging


# Configure Redis
# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

class UserRequest(BaseModel):
    user_id: str
    browsing_history: list[str]

@app.get("/")
async def home():
    return {"message": "Welcome to the Product Recommendation API"}

# Configure Redis
redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

@app.post("/recommendations")
async def get_recommendations(user_request: UserRequest):
    """Handles user requests for recommendations, with Redis caching."""

    cache_key = f"recommendations:{user_request.user_id}"
    cached_recommendations = redis_client.get(cache_key)

    if cached_recommendations:
        print(f"Cache hit for user {user_request.user_id}")
        return {"user_id": user_request.user_id, "recommendations": json.loads(cached_recommendations)}

    # Fetch products and generate recommendations
    products = get_products()
    recommendations = generate_recommendations(user_request.browsing_history, products)

    # Cache results for 1 hour
    redis_client.set(cache_key, json.dumps(recommendations))
    redis_client.expire(cache_key, 3600)

    return {"user_id": user_request.user_id, "recommendations": recommendations}