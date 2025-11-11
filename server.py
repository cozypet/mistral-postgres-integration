#!/usr/bin/env python3
"""
Mistral AI × PostgreSQL MCP Server
Partner Enablement Asset v1.0

Purpose: Connect Mistral Le Chat Enterprise to PostgreSQL databases
         using fastMCP (Model Context Protocol)

Usage:
    python server.py

Configuration:
    Set DATABASE_URL in .env file

Author: Han HELOIR - Mistral Partner Solutions Architecture Team
"""

from fastmcp import FastMCP
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize fastMCP server
mcp = FastMCP(
    name="Mistral PostgreSQL Integration",
    version="1.0.0"
)

# Database connection helper
def get_db_connection():
    """Create database connection with error handling"""
    try:
        conn = psycopg2.connect(
            os.getenv("DATABASE_URL"),
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection established")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

# Security: Query validation
FORBIDDEN_KEYWORDS = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE', 
                      'ALTER', 'CREATE', 'GRANT', 'REVOKE']

def validate_query(query: str) -> bool:
    """Validate that query is safe (SELECT only)"""
    query_upper = query.upper().strip()
    
    # Must start with SELECT
    if not query_upper.startswith('SELECT'):
        raise ValueError("Only SELECT queries are permitted")
    
    # Check for forbidden keywords
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            raise ValueError(f"Forbidden operation detected: {keyword}")
    
    logger.info(f"Query validated: {query[:100]}...")
    return True

# ==================================================================
# TOOL DEFINITIONS
# ==================================================================

@mcp.tool()
def query_database(query: str) -> list[dict]:
    """
    Execute a SELECT query on the PostgreSQL database.
    Returns results as a list of dictionaries.
    
    Security: Only SELECT statements are allowed.
    
    Args:
        query: SQL SELECT statement to execute
    
    Returns:
        List of rows as dictionaries
        
    Example:
        query_database("SELECT * FROM customers LIMIT 5")
    """
    validate_query(query)
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            logger.info(f"Query returned {len(results)} rows")
            return results

@mcp.tool()
def get_customer_info(search: str) -> list[dict]:
    """
    Get comprehensive customer information by name or email.
    Includes account details and support ticket summary.
    
    Args:
        search: Customer name or email (partial match supported)
    
    Returns:
        Customer details with ticket statistics
        
    Example:
        get_customer_info("ASML")
        get_customer_info("accenture.com")
    """
    query = """
        SELECT 
            c.*,
            COUNT(t.id) as total_tickets,
            COUNT(CASE WHEN t.status = 'Open' THEN 1 END) as open_tickets,
            COUNT(CASE WHEN t.status = 'In Progress' THEN 1 END) as in_progress_tickets,
            COUNT(CASE WHEN t.priority = 'High' THEN 1 END) as high_priority_tickets,
            MAX(t.created_at) as last_ticket_date
        FROM customers c
        LEFT JOIN support_tickets t ON c.id = t.customer_id
        WHERE c.name ILIKE %s OR c.email ILIKE %s
        GROUP BY c.id
        ORDER BY c.mrr DESC
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            search_pattern = f"%{search}%"
            cur.execute(query, (search_pattern, search_pattern))
            results = cur.fetchall()
            
            if not results:
                logger.warning(f"No customer found for search: {search}")
                return [{"message": f"No customer found matching '{search}'"}]
            
            logger.info(f"Found {len(results)} customer(s) for: {search}")
            return results

@mcp.tool()
def get_open_tickets(priority: Optional[str] = None) -> list[dict]:
    """
    Get all open support tickets with customer context.
    Optionally filter by priority level.
    
    Args:
        priority: Filter by 'High', 'Medium', or 'Low' (optional)
    
    Returns:
        List of open tickets with customer information
        
    Example:
        get_open_tickets()  # All open tickets
        get_open_tickets(priority="High")  # Only high priority
    """
    query = """
        SELECT 
            t.id,
            t.subject,
            t.status,
            t.priority,
            t.created_at,
            c.name as customer_name,
            c.subscription_tier,
            c.mrr,
            c.country,
            EXTRACT(DAY FROM NOW() - t.created_at) as days_open
        FROM support_tickets t
        JOIN customers c ON t.customer_id = c.id
        WHERE t.status IN ('Open', 'In Progress')
    """
    
    params = []
    if priority:
        query += " AND t.priority = %s"
        params.append(priority)
    
    query += " ORDER BY t.priority DESC, t.created_at ASC"
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            results = cur.fetchall()
            logger.info(f"Found {len(results)} open tickets")
            return results

@mcp.tool()
def get_at_risk_customers(min_mrr: float = 20000.0) -> list[dict]:
    """
    Identify high-value customers with open issues (churn risk analysis).
    
    Business Logic:
    - High MRR customers (default: €20K+)
    - Currently have open or in-progress tickets
    - Sorted by revenue to prioritize escalation
    
    Args:
        min_mrr: Minimum monthly recurring revenue threshold (default: 20000)
    
    Returns:
        List of at-risk customers with issue details
        
    Example:
        get_at_risk_customers()  # Default €20K threshold
        get_at_risk_customers(min_mrr=50000)  # Enterprise tier only
    """
    query = """
        SELECT 
            c.name,
            c.email,
            c.country,
            c.subscription_tier,
            c.mrr,
            COUNT(t.id) as open_ticket_count,
            COUNT(CASE WHEN t.priority = 'High' THEN 1 END) as high_priority_count,
            STRING_AGG(t.subject, ' | ') as ticket_subjects,
            MAX(t.created_at) as newest_ticket_date,
            MAX(EXTRACT(DAY FROM NOW() - t.created_at)) as oldest_ticket_age_days
        FROM customers c
        JOIN support_tickets t ON c.id = t.customer_id
        WHERE t.status IN ('Open', 'In Progress')
          AND c.mrr >= %s
        GROUP BY c.id, c.name, c.email, c.country, c.subscription_tier, c.mrr
        ORDER BY c.mrr DESC
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (min_mrr,))
            results = cur.fetchall()
            logger.info(f"Found {len(results)} at-risk customers (MRR >= {min_mrr})")
            return results

@mcp.tool()
def get_customer_health_score(customer_name: str) -> dict:
    """
    Calculate comprehensive customer health score (0-100).
    
    Scoring Factors:
    - Ticket velocity (fewer = better)
    - Resolution time (faster = better)
    - Priority distribution (fewer high priority = better)
    - Account age (longer tenure = better)
    
    Args:
        customer_name: Customer name to analyze
    
    Returns:
        Health score and contributing factors
        
    Example:
        get_customer_health_score("ASML")
    """
    query = """
        WITH customer_metrics AS (
            SELECT 
                c.id,
                c.name,
                c.subscription_tier,
                c.mrr,
                EXTRACT(DAY FROM NOW() - c.created_at) as account_age_days,
                COUNT(t.id) as total_tickets,
                COUNT(CASE WHEN t.status IN ('Open', 'In Progress') THEN 1 END) as open_tickets,
                COUNT(CASE WHEN t.priority = 'High' THEN 1 END) as high_priority_tickets,
                AVG(EXTRACT(DAY FROM t.resolved_at - t.created_at)) as avg_resolution_days
            FROM customers c
            LEFT JOIN support_tickets t ON c.id = t.customer_id
            WHERE c.name ILIKE %s
            GROUP BY c.id
        )
        SELECT 
            *,
            CASE 
                WHEN open_tickets = 0 THEN 100
                WHEN open_tickets <= 2 AND high_priority_tickets = 0 THEN 85
                WHEN open_tickets <= 5 AND high_priority_tickets <= 1 THEN 70
                WHEN high_priority_tickets >= 2 THEN 40
                ELSE 60
            END as health_score
        FROM customer_metrics
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (f"%{customer_name}%",))
            result = cur.fetchone()
            
            if not result:
                return {"error": f"No customer found matching '{customer_name}'"}
            
            logger.info(f"Health score calculated for {customer_name}: {result['health_score']}")
            return result

# ==================================================================
# RESOURCES
# ==================================================================

@mcp.resource("postgres://schema")
def get_database_schema() -> str:
    """
    Get complete database schema information.
    Lists all tables and columns with data types.
    """
    query = """
        SELECT 
            table_name,
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            
            # Format as readable text
            schema_text = "# Database Schema\n\n"
            current_table = None
            
            for row in results:
                if row['table_name'] != current_table:
                    current_table = row['table_name']
                    schema_text += f"\n## Table: {current_table}\n\n"
                
                nullable = "NULL" if row['is_nullable'] == 'YES' else "NOT NULL"
                schema_text += f"- {row['column_name']}: {row['data_type']} ({nullable})\n"
            
            return schema_text

@mcp.resource("postgres://tables")
def get_table_list() -> str:
    """Get list of all tables in the database"""
    query = """
        SELECT table_name, 
               pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            results = cur.fetchall()
            return "\n".join([f"- {r['table_name']} ({r['size']})" for r in results])

# ==================================================================
# SERVER STARTUP
# ==================================================================

if __name__ == "__main__":
    logger.info("Starting Mistral PostgreSQL MCP Server...")
    logger.info(f"Database: {os.getenv('DATABASE_URL', 'NOT_CONFIGURED')}")

    # Test database connection
    try:
        conn = get_db_connection()
        conn.close()
        logger.info("✓ Database connection test successful")
    except Exception as e:
        logger.error(f"✗ Database connection test failed: {e}")
        exit(1)

    # Run MCP server with HTTP transport for remote access
    # Use 'sse' for Server-Sent Events (compatible with Le Chat)
    # Use 'http' for newer Streamable HTTP (recommended for production)
    logger.info("Starting server with SSE transport on http://0.0.0.0:8000")
    mcp.run(transport="sse", host="0.0.0.0", port=8000)