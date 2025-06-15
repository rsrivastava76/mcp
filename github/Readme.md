# GitHub MCP Server

A Model Context Protocol (MCP) server that integrates GitHub repositories with Claude Desktop, enabling seamless interaction with your GitHub data directly through Claude.

## Features

### 🔧 **Tools**
- **Search Repositories**: Find repositories across GitHub with advanced search queries
- **Browse Repository Files**: Navigate directory structures and file listings
- **Read File Contents**: Access and display file contents with proper encoding handling
- **Create Issues**: Generate new GitHub issues with labels and descriptions
- **List User Repositories**: Get your repositories with filtering and sorting options

### 📚 **Resources**
- **GitHub Repositories**: Access your complete repository list
- **User Profile**: Retrieve your GitHub profile information
- **Repository Details**: Get comprehensive repository metadata
- **File Resources**: Direct access to specific files and directories

### 🚀 **Capabilities**
- Full GitHub API integration with authentication
- Support for both public and private repositories
- Intelligent error handling and rate limiting
- Binary file detection and handling
- UTF-8 text file content display
- Repository search with sorting and filtering

## Prerequisites

- Python 3.9 or higher
- Claude Desktop application
- GitHub Personal Access Token
- MCP 1.0.0 compatible environment

## Installation

### 1. Clone or Download
```bash
# Create project directory
mkdir github
cd github

# Save the server code as github_mcp_server.py
```

### 2. Set Up Python Environment
```bash
# Create virtual environment
python -m venv github-mcp-env

# Activate environment
# On Windows:
github-mcp-env\Scripts\activate
# On macOS/Linux:
source github-mcp-env/bin/activate

# Install dependencies
pip install httpx>=0.25.0 mcp>=1.0.0 anyio>=4.0.0
```

### 3. GitHub Authentication

#### Create Personal Access Token
1. Go to [GitHub Settings](https://github.com/settings/tokens)
2. Click **"Developer settings"** → **"Personal access tokens"** → **"Tokens (classic)"**
3. Click **"Generate new token (classic)"**
4. Configure token:
   - **Note**: "Claude Desktop MCP Integration"
   - **Expiration**: Choose appropriate duration
   - **Scopes**: Select the following:
     - ✅ `repo` (Full control of private repositories)
     - ✅ `user` (Read user profile data)
     - ✅ `public_repo` (Access public repositories)

#### Set Environment Variable
```bash
# Windows Command Prompt
set GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Windows PowerShell
$env:GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# macOS/Linux
export GITHUB_TOKEN="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# Or create .env file
echo "GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" > .env
```

## Claude Desktop Configuration

### Locate Configuration File
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

### Update Configuration
```json
{
  "mcpServers": {
    "github": {
      "command": "python",
      "args": ["C:\\full\\path\\to\\github_mcp_server.py"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
      }
    }
  }
}
```

**Important**: 
- Use **absolute paths** for the Python script
- Replace `C:\\full\\path\\to\\` with your actual file path
- Use forward slashes `/` on macOS/Linux
- Use double backslashes `\\` on Windows

### Restart Claude Desktop
After updating the configuration, restart Claude Desktop completely to load the MCP server.

## Usage Examples

Once configured, you can interact with GitHub through Claude using natural language:

### Repository Management
```
"Show me all my GitHub repositories"
"List my private repositories sorted by last update"
"Search for Python machine learning repositories"
```

### File Operations
```
"Get the contents of README.md from my project-name repository"
"Show me the file structure of my web-app repository"
"What's in the src/main.py file in my python-project?"
```

### Issue Creation
```
"Create an issue in my project-name repository titled 'Bug: Login not working' with description 'Users cannot log in after the latest update'"
```

### Repository Exploration
```
"What are the most popular JavaScript repositories on GitHub?"
"Show me the details of the microsoft/vscode repository"
"Browse the files in the docs folder of my project"
```

## Testing

### Test Server Directly
```bash
# Activate virtual environment
source github-mcp-env/bin/activate  # Windows: github-mcp-env\Scripts\activate

# Run server
python server.py
```

## Troubleshooting

### Common Issues

#### "GITHUB_TOKEN not found" Warning
- **Solution**: Set the `GITHUB_TOKEN` environment variable
- **Check**: Verify token has correct permissions (`repo`, `user` scopes)

#### "Server not responding" in Claude Desktop
- **Solution**: Check file paths in `claude_desktop_config.json`
- **Verify**: Python executable is accessible
- **Restart**: Claude Desktop after configuration changes

#### "HTTP 401 Unauthorized" Errors
- **Solution**: Regenerate GitHub Personal Access Token
- **Check**: Token hasn't expired
- **Verify**: Token has required scopes

#### "Module not found" Errors
- **Solution**: Ensure virtual environment is activated
- **Install**: Required dependencies with correct versions
- **Check**: Python version compatibility (3.9+)

### Debugging

Enable debug logging by modifying the script:
```python
logging.basicConfig(level=logging.DEBUG)
```

Check Claude Desktop logs:
- **Windows**: `%APPDATA%\Claude\logs\`
- **macOS**: `~/Library/Logs/Claude/`

## API Rate Limits

GitHub API has rate limits:
- **Authenticated requests**: 5,000 per hour
- **Unauthenticated requests**: 60 per hour

The server automatically handles rate limiting and provides informative error messages.

## Security Considerations

- Keep your GitHub token secure and never commit it to version control
- Use tokens with minimal required permissions
- Regularly rotate your access tokens
- Monitor token usage in GitHub Settings

## Advanced Configuration

### Custom GitHub Enterprise
For GitHub Enterprise Server, modify the `base_url`:
```python
self.base_url = "https://your-github-enterprise.com/api/v3"
```

### Proxy Configuration
Add proxy support by modifying the `httpx.AsyncClient`:
```python
async with httpx.AsyncClient(proxies="http://proxy:8080") as client:
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review Claude Desktop MCP documentation
- GitHub API documentation: https://docs.github.com/en/rest
- MCP documentation: https://docs.anthropic.com/en/docs/mcp

---