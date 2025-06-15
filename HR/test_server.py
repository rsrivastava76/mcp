#!/usr/bin/env python3
"""
Simple test script to verify database connectivity
"""
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error


def test_connection():
    load_dotenv()

    config = {
        'host': os.getenv("DB_HOST", ""),
        'port': int(os.getenv("DB_PORT", "3306")),
        'user': os.getenv("DB_USER", ""),
        'password': os.getenv("DB_PASSWORD", ""),
        'database': os.getenv("DB_NAME", "")
    }

    try:
        connection = mysql.connector.connect(**config)
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees")
            count = cursor.fetchone()[0]
            print(f"✅ Database connection successful!")
            print(f"✅ Found {count} employees in the database")
            return True
    except Error as e:
        print(f"❌ Database connection failed: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    test_connection()