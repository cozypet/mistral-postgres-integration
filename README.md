# Mistral AI × PostgreSQL MCP Server

A Model Context Protocol (MCP) server that connects Mistral Le Chat Enterprise to PostgreSQL databases using FastMCP.

## Features

- **Customer Information Queries**: Search and retrieve customer details
- **Support Ticket Management**: View and analyze support tickets
- **Churn Risk Analysis**: Identify at-risk high-value customers
- **Customer Health Scoring**: Calculate comprehensive health metrics
- **Database Schema Introspection**: Dynamic schema discovery

## Tools Available

1. `query_database(query)` - Execute SELECT queries safely
2. `get_customer_info(search)` - Search customers by name/email
3. `get_open_tickets(priority)` - View support tickets by priority
4. `get_at_risk_customers(min_mrr)` - Identify churn risks
5. `get_customer_health_score(customer_name)` - Calculate health metrics

## Deployment

### Deploy to FastMCP Cloud

1. Push this repository to GitHub
2. Visit [fastmcp.cloud](https://fastmcp.cloud)
3. Sign in with GitHub
4. Create a new project:
   - Select this repository
   - Set entrypoint: `server.py:mcp`
   - Add environment variable: `DATABASE_URL` (your PostgreSQL connection string)
5. Deploy!

Your server will be available at: `https://your-project.fastmcp.app/mcp`

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL

# Run server
python server.py
```

## Configuration

Set the following environment variable:

- `DATABASE_URL`: PostgreSQL connection string (required)
- `LOG_LEVEL`: Logging level (default: INFO)

## Security

- Only SELECT queries are permitted
- Forbidden operations: DROP, DELETE, UPDATE, INSERT, TRUNCATE, ALTER, CREATE, GRANT, REVOKE
- All queries are validated before execution

## Author

Han HELOIR - Mistral Partner Solutions Architecture Team

## License

Partner Enablement Asset v1.0
