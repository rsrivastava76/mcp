#!/usr/bin/env python3
"""
HR Management MCP Server
A Model Context Protocol server for HR management system with MySQL support.
Provides read-only access to HR data through SELECT queries only.
"""

import asyncio
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional, Sequence

import mysql.connector
from mysql.connector import Error

# MCP imports
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration class"""

    def __init__(self):
        self.host = os.getenv("DB_HOST", "localhost")
        self.port = int(os.getenv("DB_PORT", "3306"))
        self.user = os.getenv("DB_USER", "root")
        self.password = os.getenv("DB_PASSWORD", "")
        self.database = os.getenv("DB_NAME", "hr_management")


class HRManagementServer:
    """HR Management MCP Server implementation"""

    def __init__(self):
        self.db_config = DatabaseConfig()
        self.server = Server("hr-management-server")
        self.setup_handlers()

    def create_connection(self):
        """Create a MySQL database connection"""
        try:
            connection = mysql.connector.connect(
                host=self.db_config.host,
                port=self.db_config.port,
                user=self.db_config.user,
                password=self.db_config.password,
                database=self.db_config.database,
                autocommit=True
            )
            if connection.is_connected():
                return connection
        except Error as e:
            logger.error(f"Database connection failed: {e}")
            raise Exception(f"Database connection failed: {e}")

    def setup_handlers(self):
        """Setup MCP request handlers"""

        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="query_employees",
                    description="Query employee information from the database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL SELECT query to execute (SELECT statements only)"
                            },
                            "limit": {
                                "type": "number",
                                "description": "Maximum number of results to return (default: 100)",
                                "default": 100
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="list_tables",
                    description="List all available tables in the HR database",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                types.Tool(
                    name="describe_table",
                    description="Get column information for a specific table",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "table_name": {
                                "type": "string",
                                "description": "Name of the table to describe"
                            }
                        },
                        "required": ["table_name"]
                    }
                ),
                types.Tool(
                    name="get_employee_by_id",
                    description="Get employee details by employee ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "employee_id": {
                                "type": "number",
                                "description": "Employee ID to lookup"
                            }
                        },
                        "required": ["employee_id"]
                    }
                ),
                types.Tool(
                    name="get_employees_by_department",
                    description="Get all employees in a specific department",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "department_name": {
                                "type": "string",
                                "description": "Name of the department"
                            }
                        },
                        "required": ["department_name"]
                    }
                ),
                types.Tool(
                    name="get_employee_count",
                    description="Get total count of employees by status",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "status": {
                                "type": "string",
                                "description": "Employee status (active, inactive, terminated)",
                                "default": "active"
                            }
                        }
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            try:
                if name == "query_employees":
                    return await self.handle_custom_query(
                        arguments.get("query"),
                        arguments.get("limit", 100)
                    )
                elif name == "list_tables":
                    return await self.handle_list_tables()
                elif name == "describe_table":
                    return await self.handle_describe_table(
                        arguments.get("table_name")
                    )
                elif name == "get_employee_by_id":
                    return await self.handle_get_employee_by_id(
                        arguments.get("employee_id")
                    )
                elif name == "get_employees_by_department":
                    return await self.handle_get_employees_by_department(
                        arguments.get("department_name")
                    )
                elif name == "get_employee_count":
                    return await self.handle_get_employee_count(
                        arguments.get("status", "active")
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")

            except Exception as e:
                logger.error(f"Tool execution error: {e}")
                return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    async def handle_custom_query(self, query: str, limit: int = 100) -> list[types.TextContent]:
        """Handle custom SQL queries (SELECT only)"""
        if not query:
            raise ValueError("Query parameter is required")

        # Security: Only allow SELECT statements
        trimmed_query = query.strip().lower()
        if not trimmed_query.startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        # Prevent potentially dangerous operations
        dangerous_keywords = ["drop", "delete", "update", "insert", "alter", "create", "truncate"]
        if any(keyword in trimmed_query for keyword in dangerous_keywords):
            raise ValueError("Query contains forbidden operations")

        connection = None
        try:
            connection = self.create_connection()
            cursor = connection.cursor(dictionary=True)

            # Add LIMIT if not present
            if "limit" not in trimmed_query:
                query += f" LIMIT {limit}"

            cursor.execute(query)
            results = cursor.fetchall()

            return [types.TextContent(
                type="text",
                text=f"Query executed successfully. Found {len(results)} results:\n\n{json.dumps(results, indent=2, default=str)}"
            )]

        except Error as e:
            raise Exception(f"Database query failed: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()

    async def handle_list_tables(self) -> list[types.TextContent]:
        """List all tables in the database"""
        connection = None
        try:
            connection = self.create_connection()
            cursor = connection.cursor()

            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]

            return [types.TextContent(
                type="text",
                text=f"Available tables in database '{self.db_config.database}':\n\n{json.dumps(tables, indent=2)}"
            )]

        except Error as e:
            raise Exception(f"Failed to list tables: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()

    async def handle_describe_table(self, table_name: str) -> list[types.TextContent]:
        """Describe table structure"""
        if not table_name:
            raise ValueError("Table name is required")

        # Basic input validation
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table_name):
            raise ValueError("Invalid table name")

        connection = None
        try:
            connection = self.create_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()

            return [types.TextContent(
                type="text",
                text=f"Table structure for '{table_name}':\n\n{json.dumps(columns, indent=2, default=str)}"
            )]

        except Error as e:
            raise Exception(f"Failed to describe table: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()

    async def handle_get_employee_by_id(self, employee_id: int) -> list[types.TextContent]:
        """Get employee details by ID"""
        if not employee_id:
            raise ValueError("Employee ID is required")

        connection = None
        try:
            connection = self.create_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT * FROM employees WHERE id = %s LIMIT 1"
            cursor.execute(query, (employee_id,))
            employee = cursor.fetchone()

            if employee:
                return [types.TextContent(
                    type="text",
                    text=f"Employee details for ID {employee_id}:\n\n{json.dumps(employee, indent=2, default=str)}"
                )]
            else:
                return [types.TextContent(
                    type="text",
                    text=f"No employee found with ID: {employee_id}"
                )]

        except Error as e:
            raise Exception(f"Failed to get employee: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()

    async def handle_get_employees_by_department(self, department_name: str) -> list[types.TextContent]:
        """Get all employees in a specific department"""
        if not department_name:
            raise ValueError("Department name is required")

        connection = None
        try:
            connection = self.create_connection()
            cursor = connection.cursor(dictionary=True)

            query = """
            SELECT e.*, d.department_name 
            FROM employees e 
            JOIN departments d ON e.department_id = d.id 
            WHERE d.department_name = %s
            """
            cursor.execute(query, (department_name,))
            employees = cursor.fetchall()

            return [types.TextContent(
                type="text",
                text=f"Employees in {department_name} department ({len(employees)} found):\n\n{json.dumps(employees, indent=2, default=str)}"
            )]

        except Error as e:
            raise Exception(f"Failed to get employees by department: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()

    async def handle_get_employee_count(self, status: str = "active") -> list[types.TextContent]:
        """Get count of employees by status"""
        connection = None
        try:
            connection = self.create_connection()
            cursor = connection.cursor(dictionary=True)

            query = "SELECT COUNT(*) as count FROM employees WHERE status = %s"
            cursor.execute(query, (status,))
            result = cursor.fetchone()

            return [types.TextContent(
                type="text",
                text=f"Number of {status} employees: {result['count']}"
            )]

        except Error as e:
            raise Exception(f"Failed to get employee count: {e}")

        finally:
            if connection and connection.is_connected():
                connection.close()


async def main():
    """Main function to run the MCP server"""
    # Load environment variables from .env file if it exists
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        logger.warning("python-dotenv not installed. Using environment variables directly.")

    # Create and run server
    server = HRManagementServer()

    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="hr-management-server",
                server_version="1.0.0",
                capabilities=server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    logger.info("Starting HR Management MCP Server...")
    asyncio.run(main())