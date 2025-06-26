#!/usr/bin/env python3

"""
Database LLM Wizard - Test Data Seeder
This script creates sample data to test our wizard's capabilities
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime, timedelta
import random

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "wizard_test", 
    "user": "wizard",
    "password": "magic123"
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)

def seed_ecommerce_data():
    """Seed e-commerce test data"""
    print("🛍️  Seeding e-commerce data...")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Create customers table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    phone VARCHAR(20),
                    address TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create products table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    price DECIMAL(10, 2) NOT NULL,
                    category VARCHAR(100),
                    stock_quantity INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create orders table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    customer_id INTEGER REFERENCES customers(id),
                    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    total_amount DECIMAL(10, 2),
                    status VARCHAR(50) DEFAULT 'pending'
                )
            """)
            
            # Insert sample customers
            customers = [
                ("Alice Johnson", "alice@example.com", "+1-555-0101", "123 Main St, Anytown, USA"),
                ("Bob Smith", "bob@example.com", "+1-555-0102", "456 Oak Ave, Somewhere, USA"),
                ("Carol Davis", "carol@example.com", "+1-555-0103", "789 Pine Rd, Elsewhere, USA"),
                ("David Wilson", "david@example.com", "+1-555-0104", "321 Elm St, Nowhere, USA"),
                ("Eve Brown", "eve@example.com", "+1-555-0105", "654 Maple Dr, Anywhere, USA")
            ]
            
            for customer in customers:
                cur.execute("""
                    INSERT INTO customers (name, email, phone, address)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (email) DO NOTHING
                """, customer)
            
            # Insert sample products
            products = [
                ("Laptop Pro", "High-performance laptop for professionals", 1299.99, "Electronics", 25),
                ("Wireless Headphones", "Premium noise-canceling headphones", 299.99, "Electronics", 50),
                ("Coffee Maker", "Automatic drip coffee maker", 89.99, "Appliances", 30),
                ("Running Shoes", "Comfortable athletic shoes", 129.99, "Sports", 40),
                ("Desk Chair", "Ergonomic office chair", 199.99, "Furniture", 15),
                ("Smartphone", "Latest model smartphone", 899.99, "Electronics", 20),
                ("Backpack", "Durable travel backpack", 59.99, "Accessories", 35),
                ("Yoga Mat", "Non-slip exercise mat", 29.99, "Sports", 60)
            ]
            
            for product in products:
                cur.execute("""
                    INSERT INTO products (name, description, price, category, stock_quantity)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, product)
            
            # Insert sample orders
            for i in range(10):
                customer_id = random.randint(1, 5)
                total_amount = round(random.uniform(50, 500), 2)
                status = random.choice(['pending', 'shipped', 'delivered', 'cancelled'])
                order_date = datetime.now() - timedelta(days=random.randint(1, 30))
                
                cur.execute("""
                    INSERT INTO orders (customer_id, order_date, total_amount, status)
                    VALUES (%s, %s, %s, %s)
                """, (customer_id, order_date, total_amount, status))
            
            conn.commit()
            print("✅ E-commerce data seeded successfully")

def seed_blog_data():
    """Seed blog test data"""
    print("📝 Seeding blog data...")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Create users table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    bio TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create posts table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    content TEXT NOT NULL,
                    author_id INTEGER REFERENCES users(id),
                    published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    view_count INTEGER DEFAULT 0,
                    tags TEXT[]
                )
            """)
            
            # Create comments table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS comments (
                    id SERIAL PRIMARY KEY,
                    post_id INTEGER REFERENCES posts(id),
                    author_id INTEGER REFERENCES users(id),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert sample users
            users = [
                ("techguru", "tech@example.com", "Passionate about technology and innovation"),
                ("foodlover", "food@example.com", "Exploring cuisines from around the world"),
                ("traveler", "travel@example.com", "Digital nomad sharing travel experiences"),
                ("bookworm", "books@example.com", "Avid reader and literature enthusiast")
            ]
            
            for user in users:
                cur.execute("""
                    INSERT INTO users (username, email, bio)
                    VALUES (%s, %s, %s)
                    ON CONFLICT (username) DO NOTHING
                """, user)
            
            # Insert sample posts
            posts = [
                ("The Future of AI", "Exploring the latest developments in artificial intelligence...", 1, ["ai", "technology"]),
                ("Best Coffee Shops in San Francisco", "A curated list of the most amazing coffee experiences...", 2, ["food", "coffee", "sf"]),
                ("Digital Nomad Guide to Thailand", "Everything you need to know about working remotely from Thailand...", 3, ["travel", "remote-work"]),
                ("Book Review: 1984 by George Orwell", "A timeless classic that feels more relevant than ever...", 4, ["books", "review"])
            ]
            
            for post in posts:
                cur.execute("""
                    INSERT INTO posts (title, content, author_id, tags, view_count)
                    VALUES (%s, %s, %s, %s, %s)
                """, (post[0], post[1], post[2], post[3], random.randint(50, 500)))
            
            conn.commit()
            print("✅ Blog data seeded successfully")

def seed_library_data():
    """Seed library test data"""
    print("📚 Seeding library data...")
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            # Create authors table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS authors (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    birth_year INTEGER,
                    nationality VARCHAR(100)
                )
            """)
            
            # Create books table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title VARCHAR(255) NOT NULL,
                    author_id INTEGER REFERENCES authors(id),
                    isbn VARCHAR(20) UNIQUE,
                    publication_year INTEGER,
                    genre VARCHAR(100),
                    available_copies INTEGER DEFAULT 1
                )
            """)
            
            # Create borrowers table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS borrowers (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    membership_date DATE DEFAULT CURRENT_DATE
                )
            """)
            
            # Insert sample authors
            authors = [
                ("George Orwell", 1903, "British"),
                ("Jane Austen", 1775, "British"),
                ("Gabriel García Márquez", 1927, "Colombian"),
                ("Haruki Murakami", 1949, "Japanese")
            ]
            
            for author in authors:
                cur.execute("""
                    INSERT INTO authors (name, birth_year, nationality)
                    VALUES (%s, %s, %s)
                """, author)
            
            # Insert sample books
            books = [
                ("1984", 1, "978-0-452-28423-4", 1949, "Dystopian Fiction", 3),
                ("Animal Farm", 1, "978-0-452-28424-1", 1945, "Political Satire", 2),
                ("Pride and Prejudice", 2, "978-0-14-143951-8", 1813, "Romance", 4),
                ("One Hundred Years of Solitude", 3, "978-0-06-088328-7", 1967, "Magical Realism", 2),
                ("Norwegian Wood", 4, "978-0-375-70463-5", 1987, "Literary Fiction", 1)
            ]
            
            for book in books:
                cur.execute("""
                    INSERT INTO books (title, author_id, isbn, publication_year, genre, available_copies)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, book)
            
            # Insert sample borrowers
            borrowers = [
                ("Michael Chen", "michael@example.com"),
                ("Sarah Williams", "sarah@example.com"), 
                ("James Rodriguez", "james@example.com")
            ]
            
            for borrower in borrowers:
                cur.execute("""
                    INSERT INTO borrowers (name, email)
                    VALUES (%s, %s)
                    ON CONFLICT (email) DO NOTHING
                """, borrower)
            
            conn.commit()
            print("✅ Library data seeded successfully")

def show_summary():
    """Show summary of seeded data"""
    print("\n📊 Database Summary:")
    
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Get table counts
            tables = ['customers', 'products', 'orders', 'users', 'posts', 'comments', 'authors', 'books', 'borrowers']
            
            for table in tables:
                try:
                    cur.execute(f"SELECT COUNT(*) as count FROM {table}")
                    count = cur.fetchone()['count']
                    print(f"   {table}: {count} records")
                except psycopg2.Error:
                    # Table doesn't exist, skip
                    pass

def main():
    """Main seeding function"""
    print("🧙‍♂️ Database LLM Wizard - Seeding Test Data")
    print("=" * 50)
    
    try:
        # Test connection
        with get_connection() as conn:
            print("✅ Connected to PostgreSQL")
        
        # Seed different data sets
        seed_ecommerce_data()
        seed_blog_data() 
        seed_library_data()
        
        # Show summary
        show_summary()
        
        print("\n🎉 All test data seeded successfully!")
        print("\nNow you can test the wizard with queries like:")
        print("  • 'Show me all customers'")
        print("  • 'Create a new product called Magic Wand'")
        print("  • 'How many books do we have by each author?'")
        print("  • 'Find all orders from the last week'")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()