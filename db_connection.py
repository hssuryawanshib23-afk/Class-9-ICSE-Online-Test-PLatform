"""
Database connection manager - works with both SQLite (local) and PostgreSQL (production)
"""
import os
import sqlite3

# Check if running on Streamlit Cloud (has secrets) or locally
USE_POSTGRES = os.getenv("USE_POSTGRES", "false").lower() == "true"

def get_connection():
    """Get database connection - PostgreSQL in production, SQLite locally"""
    if USE_POSTGRES:
        # PostgreSQL for production (Streamlit Cloud)
        import psycopg2
        import streamlit as st
        
        conn = psycopg2.connect(
            host=st.secrets["postgres"]["host"],
            database=st.secrets["postgres"]["database"],
            user=st.secrets["postgres"]["user"],
            password=st.secrets["postgres"]["password"],
            port=st.secrets["postgres"]["port"]
        )
        return conn
    else:
        # SQLite for local development
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        DB_PATH = os.path.join(BASE_DIR, "database", "quiz.db")
        return sqlite3.connect(DB_PATH)

def execute_query(query, params=None, fetch=None):
    """
    Execute a query with automatic connection handling
    
    Args:
        query: SQL query string
        params: Query parameters (tuple)
        fetch: 'one', 'all', or None
    
    Returns:
        Query results or None
    """
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        if fetch == 'one':
            result = cur.fetchone()
        elif fetch == 'all':
            result = cur.fetchall()
        else:
            result = None
        
        conn.commit()
        return result
    
    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        cur.close()
        conn.close()

def get_db_type():
    """Return current database type for debugging"""
    return "PostgreSQL" if USE_POSTGRES else "SQLite"

def get_placeholder():
    """Return the correct parameter placeholder for current database"""
    return "%s" if USE_POSTGRES else "?"

def adapt_query(query):
    """
    Adapt query syntax for current database
    Replaces PostgreSQL-specific syntax with SQLite equivalents when needed
    """
    if not USE_POSTGRES:
        # Convert PostgreSQL syntax to SQLite
        query = query.replace("RETURNING id", "")
        query = query.replace("NOW()", "CURRENT_TIMESTAMP")
        # Replace %s with ? for SQLite
        count = query.count("%s")
        for _ in range(count):
            query = query.replace("%s", "?", 1)
    return query

def get_last_insert_id(cursor, conn):
    """Get the last inserted ID in a database-agnostic way"""
    if USE_POSTGRES:
        # PostgreSQL returns ID from RETURNING clause
        return cursor.fetchone()[0]
    else:
        # SQLite uses lastrowid
        return cursor.lastrowid
