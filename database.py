from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

# PostgreSQL Database URL
DATABASE_URL = "postgresql://postgres:Pass123@localhost:5432/productdb"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    description = Column(String)
    price = Column(Float)

def initialize_database():
    """Creates PostgreSQL database tables and loads products from JSON."""
    print("Initializing database...")

    Base.metadata.create_all(bind=engine)  # Ensure tables exist

    session = SessionLocal()
    
    try:
        with open('data/products.json', 'r') as file:
            products = json.load(file)
            for product in products:
                existing_product = session.query(Product).filter_by(id=product['id']).first()
                if not existing_product:
                    new_product = Product(
                        id=product['id'],
                        name=product['name'],
                        category=product['category'],
                        description=product['description'],
                        price=product['price']
                    )
                    session.add(new_product)
        session.commit()
        print("Products inserted successfully!")
    except Exception as e:
        print(f"Error inserting data: {e}")
    finally:
        session.close()

# Run database initialization
initialize_database()