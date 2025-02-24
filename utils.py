from transformers import pipeline
import json
from database import SessionLocal, Product  # Import SQLAlchemy session
import os
import openai
import faiss
import numpy as np

def get_products():
    """Fetch all products from PostgreSQL database."""
    session = SessionLocal()
    
    # Fetch all products using SQLAlchemy
    products = session.query(Product).all()
    
    # Convert product objects to dictionaries
    product_list = [{"id": p.id, "name": p.name, "category": p.category, "description": p.description, "price": p.price} for p in products]

    session.close()

    print("Fetched products:", product_list)  # Debugging line
    return product_list

def generate_recommendations(browsing_history, products):
    """Generates recommendations using Hugging Face GPT-2 and filters them correctly."""
    
    # Initialize the text generation pipeline
    generator = pipeline('text-generation', model='gpt2')

    # Extract product names
    product_names = [p["name"] for p in products]

    # Create a prompt for the LLM to generate recommendations
    prompt = (
        f"Recommend 3 products from the following list: {', '.join(product_names)} "
        f"for a user interested in {', '.join(browsing_history)}. "
        "Respond ONLY with a JSON array of product names."
    )

    print("DEBUG: LLM Prompt:", prompt)

    # Generate recommendations using the LLM
    generated_text = generator(prompt, max_new_tokens=100, num_return_sequences=1)

    print("DEBUG: LLM Output:", generated_text)

    # Extract valid product names from the LLM output
    try:
        # Parse the generated text as JSON
        generated_products = json.loads(generated_text[0]["generated_text"])
    except json.JSONDecodeError:
        # If the output is not valid JSON, return an empty list
        generated_products = []

    # Filter the products based on the LLM's recommendations
    recommended_products = [
        p for p in products if p["name"] in generated_products
    ]

    print("DEBUG: Filtered Recommendations:", recommended_products)
    return recommended_products[:5]  # Limit to 5 recommendations


# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# openai.api_key = OPENAI_API_KEY

# def get_embedding(text):
#     """Generates an embedding vector for the given text using OpenAI."""
#     response = openai.Embedding.create(
#         input=text,
#         model="text-embedding-ada-002"
#     )
#     return response["data"][0]["embedding"]

# def build_faiss_index(products):
#     """Builds a FAISS index for product similarity search."""
#     product_embeddings = [get_embedding(p["description"]) for p in products]
#     index = faiss.IndexFlatL2(len(product_embeddings[0]))
#     index.add(np.array(product_embeddings, dtype=np.float32))
#     return index, product_embeddings

# def generate_recommendations(browsing_history, products):
#     """Generates recommendations using FAISS similarity search."""
    
#     index, product_embeddings = build_faiss_index(products)

#     # Convert browsing history to embedding
#     user_embedding = get_embedding(", ".join(browsing_history))

#     # Find the closest matches in FAISS
#     D, I = index.search(np.array([user_embedding], dtype=np.float32), k=5)

#     # Retrieve recommended products
#     recommended_products = [products[i] for i in I[0]]

#     print("DEBUG: Filtered Recommendations:", recommended_products)
#     return recommended_products