#!/usr/bin/env python3
"""
Script to recreate the database with the updated schema
"""
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.app.models.chat import Base
from backend.app.utils.db import engine

def recreate_database():
    print("Creating database tables with updated schema...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")
    print("Tables created:")
    for table_name in Base.metadata.tables.keys():
        print(f"  - {table_name}")

if __name__ == "__main__":
    recreate_database()
