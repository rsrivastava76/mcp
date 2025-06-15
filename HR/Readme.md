# HR Management MCP Server Setup Guide (Python)

This guide will walk you through setting up a Python MCP server for your HR management system with MySQL integration.

## Prerequisites

- Python 3.8+ installed
- MySQL database with your HR data
- Claude Desktop application
- pip package manager

## Step 1: Project Setup

1. Create a new directory for your MCP server:
```bash
mkdir hr-mcp-server
cd hr-mcp-server
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. Create the project structure:
```bash
mkdir src
touch src/__init__.py
```

4. Save the main server code as `src/hr_server.py`

## Step 2: Install Dependencies

1. Create a `requirements.txt` file (provided above)

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Step 3: Database Configuration

1. Create a `.env` file in your project root:
```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_NAME=hr_management
```

2. Update the values with your actual database credentials.

## Step 4: Sample Database Schema

Create your HR database with this sample schema:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS hr_management;
USE hr_management;

-- Departments table
CREATE TABLE departments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    manager_id INT,
    budget DECIMAL(12,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Employees table
CREATE TABLE employees (
    id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id VARCHAR(20) UNIQUE NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    hire_date DATE NOT NULL,
    job_title VARCHAR(100) NOT NULL,
    department_id INT,
    salary DECIMAL(10,2),
    manager_id INT,
    status ENUM('active', 'inactive', 'terminated') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);

-- Insert sample departments
INSERT INTO departments (department_name, description, budget) VALUES
('Human Resources', 'Manages employee relations and policies', 500000.00),
('Engineering', 'Software development and technical operations', 2000000.00),
('Marketing', 'Brand promotion and customer acquisition', 800000.00),
('Finance', 'Financial planning and accounting', 600000.00),
('Operations', 'Day-to-day business operations', 750000.00);

-- Insert sample employees
INSERT INTO employees (employee_id, first_name, last_name, email, phone, hire_date, job_title, department_id, salary, status) VALUES
('EMP001', 'John', 'Doe', 'john.doe@company.com', '+1-555-0101', '2023-01-15', 'Software Engineer', 2, 75000.00, 'active'),
('EMP002', 'Jane', 'Smith', 'jane.smith@company.com', '+1-555-0102', '2023-02-20', 'HR Manager', 1, 80000.00, 'active'),
('EMP003', 'Mike', 'Johnson', 'mike.johnson@company.com', '+1-555-0103', '2023-03-10', 'Marketing Specialist', 3, 60000.00, 'active'),
('EMP004', 'Sarah', 'Wilson', 'sarah.wilson@company.com', '+1-555-0104', '2023-04-05', 'Financial Analyst', 4, 65000.00, 'active'),
('EMP005', 'David', 'Brown', 'david.brown@company.com', '+1-555-0105', '2023-05-12', 'Operations Manager', 5, 85000.00, 'active'),
('EMP006', 'Lisa', 'Davis', 'lisa.davis@company.com', '+1-555-0106', '2023-06-08', 'Senior Developer', 2, 90000.00, 'active'),
('EMP007', 'Tom', 'Miller', 'tom.miller@company.com', '+1-555-0107', '2022-12-01', 'Marketing Director', 3, 95000.00, 'active'),
('EMP008', 'Amy', 'Garcia', 'amy.garcia@company.com', '+1-555-0108', '2023-07-15', 'HR Specialist', 1, 55000.00, 'active');
```

## Step 5: Test the Server

1. Run the test:
```bash
python test_server.py
```

## Step 6: Configure Claude Desktop

1. Open your Claude Desktop configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Add your MCP server configuration:
```json
{
  "mcpServers": {
    "hr-management": {
      "command": "python",
      "args": ["/absolute/path/to/your/hr-mcp-server/src/hr_server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "your_mysql_username",
        "DB_PASSWORD": "your_mysql_password",
        "DB_NAME": "hr_management"
      }
    }
  }
}
```

**Important**: Use the absolute path to your Python script file.

### Alternative Configuration (Using Virtual Environment)

If you're using a virtual environment, you can also configure it like this:

```json
{
  "mcpServers": {
    "hr-management": {
      "command": "/absolute/path/to/your/hr-mcp-server/venv/bin/python",
      "args": ["/absolute/path/to/your/hr-mcp-server/src/hr_server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_USER": "your_mysql_username",
        "DB_PASSWORD": "your_mysql_password",
        "DB_NAME": "hr_management"
      }
    }
  }
}
```

## Step 7: Restart Claude Desktop

Restart Claude Desktop to load your new MCP server.

## Available Tools

Your MCP server provides these tools:

1. **query_employees**: Execute custom SELECT queries
2. **list_tables**: View all database tables
3. **describe_table**: Get table schema information
4. **get_employee_by_id**: Find specific employee by ID
5. **get_employees_by_department**: Get all employees in a department
6. **get_employee_count**: Count employees by status

## Example Usage in Claude Desktop

Once configured, you can ask Claude:

- "Show me all employees in the Engineering department"
- "What's the structure of the employees table?"
- "How many active employees do we have?"
- "Find employee with ID 5"
- "List all employees hired after January 2023"
- "Show me the average salary by department"

## Security Features

- **Read-only access**: Only SELECT queries allowed
- **SQL injection protection**: Parameterized queries and input validation
- **Query limits**: Automatic limits to prevent large result sets
- **Input sanitization**: Table name validation
- **Error handling**: Comprehensive error handling and logging

## Troubleshooting

### Common Issues:

1. **ImportError: No module named 'mcp'**
   ```bash
   pip install mcp>=1.0.0
   ```

2. **Database connection failed**
   - Check your database credentials in `.env`
   - Ensure MySQL server is running
   - Verify database exists and user has permissions

3. **Claude Desktop not loading the server**
   - Check the configuration file syntax
   - Verify file paths are absolute
   - Check Claude Desktop logs for errors

4. **Permission denied errors**
   - Ensure Python script has execute permissions:
     ```bash
     chmod +x src/hr_server.py
     ```

### Debugging Steps:

1. Test database connection:
   ```bash
   python test_server.py
   ```

2. Run the server manually to check for errors:
   ```bash
   python src/hr_server.py
   ```

3. Check Claude Desktop logs:
   - **macOS**: `~/Library/Logs/Claude/`
   - **Windows**: `%APPDATA%\Claude\Logs\`

## Extending the Server

You can easily extend this server by:

1. **Adding new tools**: Add new handler methods and register them in `handle_list_tools()`

2. **Custom business logic**: Create specialized queries for common HR operations

3. **Multiple databases**: Modify the connection logic to support multiple databases

4. **Caching**: Add Redis-based caching for frequently accessed data

5. **Data validation**: Add more sophisticated input validation

## Production Considerations

- Use connection pooling for better performance
- Implement proper logging and monitoring
- Add rate limiting to prevent abuse
- Use environment-specific configurations
- Set up proper backup procedures
- Consider using read replicas for large databases

Your HR MCP server is now ready to integrate with Claude Desktop!