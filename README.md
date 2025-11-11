# Mistral AI × PostgreSQL MCP Server

> **Partner Enablement Asset** - Connect Mistral Le Chat Enterprise to PostgreSQL databases using the Model Context Protocol (MCP)

A production-ready MCP server that enables natural language queries against PostgreSQL databases through Mistral Le Chat, built with FastMCP for seamless integration and deployment.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Quick Start](#quick-start)
- [Deployment Guide](#deployment-guide)
- [Integration with Le Chat](#integration-with-le-chat)
- [Available Tools](#available-tools)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This MCP server bridges the gap between Mistral Le Chat and PostgreSQL databases, enabling business users to query and analyze data using natural language. Built for enterprise use cases like customer success, support operations, and business intelligence.

**Key Capabilities:**
- Natural language database queries via Le Chat
- Pre-built business intelligence tools
- Secure, read-only access with query validation
- Serverless deployment with FastMCP Cloud
- Compatible with any PostgreSQL database (local, Neon, AWS RDS, etc.)

---

## 🏗️ Architecture

```
┌─────────────────┐         ┌──────────────────┐         ┌─────────────────┐
│  Mistral        │         │   FastMCP Cloud  │         │   PostgreSQL    │
│  Le Chat        │ ◄─────► │   MCP Server     │ ◄─────► │   Database      │
│  Enterprise     │   MCP   │   (server.py)    │   SQL   │   (Neon)        │
└─────────────────┘         └──────────────────┘         └─────────────────┘
     User Query         HTTP/SSE Transport          Validated Queries
```

**Components:**
1. **Le Chat Frontend**: Natural language interface for business users
2. **MCP Server**: FastMCP-based server exposing database tools
3. **PostgreSQL**: Backend database (Neon serverless in this demo)

---

## ✨ Features

### Business Intelligence Tools
- **Customer 360 View**: Comprehensive customer information with support history
- **Support Ticket Analytics**: Real-time ticket monitoring and filtering
- **Churn Risk Detection**: Identify high-value at-risk customers automatically
- **Health Score Calculation**: Multi-factor customer health assessment
- **Ad-hoc Queries**: Safe SQL execution for custom analysis

### Technical Features
- **Security-First Design**: Read-only access with query validation
- **SSE Transport**: Server-Sent Events for efficient communication
- **Auto-scaling**: Serverless deployment handles variable load
- **Schema Discovery**: Dynamic database introspection
- **Error Handling**: Comprehensive logging and error management

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL database (local or cloud)
- GitHub account (for FastMCP Cloud deployment)
- Mistral Le Chat Enterprise access

### Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/mistral-postgres-integration.git
cd mistral-postgres-integration

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure database connection
cp .env.example .env
# Edit .env and set your DATABASE_URL

# 5. Run the server
python server.py
```

The server will start on `http://0.0.0.0:8000` with SSE transport.

---

## 🌐 Deployment Guide

### Option 1: FastMCP Cloud (Recommended)

FastMCP Cloud provides zero-configuration deployment with automatic scaling.

#### Step 1: Prepare Database

**Using Neon (Recommended for demos):**
1. Sign up at [neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string (format: `postgresql://user:pass@host/db?sslmode=require`)
4. Run the schema setup:

```sql
-- Create tables
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    country VARCHAR(50),
    subscription_tier VARCHAR(20),
    mrr DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE support_tickets (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(id),
    subject VARCHAR(200),
    status VARCHAR(20),
    priority VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Insert sample data (see setup_neon.sql for full dataset)
```

#### Step 2: Deploy to FastMCP Cloud

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/mistral-postgres-integration.git
   git push -u origin main
   ```

2. **Configure FastMCP Cloud**
   - Visit [fastmcp.cloud](https://fastmcp.cloud)
   - Sign in with GitHub
   - Click "Create Project"
   - Select your repository
   - Configure:
     - **Name**: `mistral-postgres-integration`
     - **Entrypoint**: `server.py:mcp`
     - **Environment Variables**:
       - Key: `DATABASE_URL`
       - Value: Your PostgreSQL connection string
   - Click "Deploy"

3. **Verify Deployment**
   - Wait for build to complete (2-3 minutes)
   - Note your server URL: `https://your-project.fastmcp.app/mcp`
   - Check logs for successful database connection

#### Step 3: Important Notes

**Database Connection String Format:**
- Remove `channel_binding=require` parameter if present
- Use format: `postgresql://user:pass@host:5432/db?sslmode=require`

**Common Issues:**
- If deployment fails, check FastMCP Cloud logs
- Ensure `DATABASE_URL` environment variable is set
- Verify Neon database is accessible (not restricted by IP)

---

## 🔌 Integration with Le Chat

Once your MCP server is deployed, connect it to Mistral Le Chat Enterprise.

### Step 1: Access Connectors

1. Open [Le Chat](https://chat.mistral.ai)
2. Click the **Intelligence** panel (sidebar)
3. Navigate to **Connectors**
4. Click **"+ Add Connector"**

### Step 2: Configure Custom Connector

In the Custom MCP Connector form:

- **Connector Name**: `postgresql-integration` (no spaces or special characters)
- **Connection Server**: `https://your-project.fastmcp.app/mcp`
- **Description**: `Query PostgreSQL customer database - access customer info, support tickets, and business analytics`
- **Authentication Method**: `No Authentication` (or configure bearer token if needed)

Click **"Connect"** to establish the connection.

### Step 3: Set Function Permissions

After connection:
1. Go to **My Connectors** tab
2. Click on your connector card
3. Navigate to **Functions** tab
4. Toggle **"Always Allow"** for frequently used functions to avoid repetitive permission prompts

### Step 4: Test Integration

Try these example queries in Le Chat:

```
Show me all customers in France with Enterprise subscriptions

What are the high priority support tickets currently open?

Get detailed information for ASML including their ticket history

Which high-value customers (>50K MRR) have open issues?

Calculate the health score for Accenture
```

---

## 🛠️ Available Tools

### 1. `query_database(query: str)`
Execute custom SELECT queries with safety validation.

**Example:**
```python
query_database("SELECT name, country, mrr FROM customers WHERE subscription_tier = 'Enterprise' ORDER BY mrr DESC LIMIT 10")
```

**Returns:** List of rows as dictionaries

---

### 2. `get_customer_info(search: str)`
Search customers by name or email with comprehensive details.

**Parameters:**
- `search`: Customer name or email (supports partial matching)

**Example:**
```python
get_customer_info("ASML")
get_customer_info("accenture.com")
```

**Returns:** Customer details + ticket statistics (total, open, high priority, last ticket date)

---

### 3. `get_open_tickets(priority: Optional[str])`
Retrieve all open support tickets with customer context.

**Parameters:**
- `priority`: Filter by 'High', 'Medium', or 'Low' (optional)

**Example:**
```python
get_open_tickets()           # All open tickets
get_open_tickets("High")     # Only high priority
```

**Returns:** List of tickets with customer name, subscription tier, MRR, days open

---

### 4. `get_at_risk_customers(min_mrr: float = 20000.0)`
Identify high-value customers with unresolved issues (churn risk).

**Parameters:**
- `min_mrr`: Minimum monthly recurring revenue threshold (default: €20K)

**Example:**
```python
get_at_risk_customers()           # Default €20K threshold
get_at_risk_customers(50000)      # Enterprise tier only
```

**Returns:** Customers with MRR >= threshold + open ticket details, sorted by revenue

---

### 5. `get_customer_health_score(customer_name: str)`
Calculate comprehensive health score (0-100) based on support metrics.

**Scoring Factors:**
- Ticket velocity (fewer = better)
- Priority distribution (fewer high priority = better)
- Resolution patterns
- Account tenure

**Example:**
```python
get_customer_health_score("ASML")
```

**Returns:** Health score + contributing metrics

---

### 6. Resource: `postgres://schema`
Retrieve complete database schema (tables, columns, types).

**Example:** "Show me the database schema"

---

### 7. Resource: `postgres://tables`
List all tables with sizes.

**Example:** "What tables are available?"

---

## 🔒 Security

### Query Validation
All queries are validated before execution:
- **Allowed**: `SELECT` statements only
- **Forbidden**: `DROP`, `DELETE`, `UPDATE`, `INSERT`, `TRUNCATE`, `ALTER`, `CREATE`, `GRANT`, `REVOKE`

### Implementation
```python
def validate_query(query: str) -> bool:
    query_upper = query.upper().strip()
    if not query_upper.startswith('SELECT'):
        raise ValueError("Only SELECT queries are permitted")

    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            raise ValueError(f"Forbidden operation: {keyword}")

    return True
```

### Best Practices
- Use read-only database user credentials
- Store `DATABASE_URL` as environment variable (never commit to git)
- Enable SSL/TLS for database connections (`sslmode=require`)
- Monitor query logs for suspicious activity
- Implement rate limiting in production environments

---

## 🐛 Troubleshooting

### Issue: Database Connection Fails in FastMCP Cloud

**Error:** `connection to server on socket "/var/run/..."`

**Solutions:**
1. Verify `DATABASE_URL` environment variable is set in FastMCP Cloud configuration
2. Remove `channel_binding=require` from connection string
3. Check Neon database allows connections from any IP
4. Verify connection string format: `postgresql://user:pass@host:5432/db?sslmode=require`

---

### Issue: Le Chat Shows "Tool Execution Failed"

**Solutions:**
1. Check FastMCP Cloud logs for errors
2. Verify database contains the expected tables (customers, support_tickets)
3. Test queries manually using the FastMCP Cloud inspector
4. Ensure database user has SELECT permissions

---

### Issue: Connector Not Appearing in Le Chat

**Solutions:**
1. Verify you have admin privileges in Le Chat Enterprise
2. Check that the MCP server URL is accessible (test in browser)
3. Try removing and re-adding the connector
4. Contact Mistral support if issue persists

---

## 📊 Sample Data

The demo includes realistic European enterprise customer data:

**Customers:**
- Accenture Technology Solutions (France, €50K MRR)
- ASML Holding (Netherlands, €75K MRR)
- BNP Paribas Digital (France, €60K MRR)
- Volkswagen Group (Germany, €80K MRR)
- And more...

**Ticket Types:**
- SSO configuration issues
- API rate limits
- Compliance documentation
- Training requests
- Security audits

---

## 🤝 Contributing

This is a partner enablement asset. For questions or improvements:
- Open an issue on GitHub
- Contact: han.heloir@mistral.ai
- Mistral Partner Solutions Architecture Team

---

## 📄 License

Partner Enablement Asset v1.0
© 2024 Mistral AI

---

## 🔗 Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [Model Context Protocol Spec](https://modelcontextprotocol.io)
- [Mistral Le Chat Custom Connectors](https://help.mistral.ai/en/articles/393572-configuring-a-custom-connector)
- [Neon PostgreSQL](https://neon.tech)

---

**Built with ❤️ by the Mistral Partner Solutions Architecture Team**
