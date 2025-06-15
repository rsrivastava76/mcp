#!/usr/bin/env python3
"""
GitHub MCP Server for MCP 1.0.0
Integrates GitHub repositories with Claude Desktop via MCP protocol
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional
import httpx
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio
from dotenv import load_dotenv

# Load .env file from current directory
load_dotenv(dotenv_path="github/.env.github")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("github-mcp-server")


class GitHubMCPServer:
    def __init__(self):
        self.server = Server("github-mcp-server")
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"

        if not self.github_token:
            logger.warning("GITHUB_TOKEN not found. Some operations may be limited.")

        self.setup_handlers()

    def setup_handlers(self):
        """Setup MCP protocol handlers"""

        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """List available GitHub resources"""
            return [
                Resource(
                    uri="github://repositories",
                    name="GitHub Repositories",
                    description="List of user's GitHub repositories",
                    mimeType="application/json",
                ),
                Resource(
                    uri="github://user",
                    name="GitHub User Profile",
                    description="Authenticated user's GitHub profile",
                    mimeType="application/json",
                ),
            ]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read GitHub resource content"""
            if uri == "github://repositories":
                return await self.get_repositories()
            elif uri == "github://user":
                return await self.get_user_profile()
            elif uri.startswith("github://repo/"):
                # Extract repo info from URI: github://repo/owner/name
                parts = uri.split("/")
                if len(parts) >= 4:
                    owner, repo = parts[2], parts[3]
                    return await self.get_repository_details(owner, repo)
            elif uri.startswith("github://file/"):
                # Extract file info: github://file/owner/repo/path
                parts = uri.split("/", 4)
                if len(parts) >= 5:
                    owner, repo, path = parts[2], parts[3], parts[4]
                    return await self.get_file_content(owner, repo, path)

            raise ValueError(f"Unknown resource URI: {uri}")

        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """List available GitHub tools"""
            return [
                Tool(
                    name="search_repositories",
                    description="Search GitHub repositories",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for repositories"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    },
                ),
                Tool(
                    name="get_repository_files",
                    description="Get files and directory structure of a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Repository owner"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository name"
                            },
                            "path": {
                                "type": "string",
                                "description": "Path within repository (optional)",
                                "default": ""
                            }
                        },
                        "required": ["owner", "repo"]
                    },
                ),
                Tool(
                    name="get_file_content",
                    description="Get content of a specific file from a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Repository owner"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository name"
                            },
                            "path": {
                                "type": "string",
                                "description": "File path within repository"
                            },
                            "ref": {
                                "type": "string",
                                "description": "Git reference (branch, tag, or commit SHA)",
                                "default": "main"
                            }
                        },
                        "required": ["owner", "repo", "path"]
                    },
                ),
                Tool(
                    name="create_issue",
                    description="Create a new issue in a repository",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "owner": {
                                "type": "string",
                                "description": "Repository owner"
                            },
                            "repo": {
                                "type": "string",
                                "description": "Repository name"
                            },
                            "title": {
                                "type": "string",
                                "description": "Issue title"
                            },
                            "body": {
                                "type": "string",
                                "description": "Issue description"
                            },
                            "labels": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Issue labels (optional)"
                            }
                        },
                        "required": ["owner", "repo", "title"]
                    },
                ),
                Tool(
                    name="list_user_repos",
                    description="List repositories for the authenticated user",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "type": {
                                "type": "string",
                                "enum": ["all", "owner", "public", "private", "member"],
                                "description": "Type of repositories to list",
                                "default": "all"
                            },
                            "sort": {
                                "type": "string",
                                "enum": ["created", "updated", "pushed", "full_name"],
                                "description": "Sort repositories by",
                                "default": "updated"
                            },
                            "per_page": {
                                "type": "integer",
                                "description": "Number of results per page (max 100)",
                                "default": 30,
                                "maximum": 100
                            }
                        }
                    },
                ),
            ]

        @self.server.call_tool()
        async def handle_call_tool(
                name: str, arguments: dict[str, Any]
        ) -> list[TextContent]:
            """Handle tool calls"""
            try:
                if name == "search_repositories":
                    result = await self.search_repositories(
                        arguments["query"],
                        arguments.get("limit", 10)
                    )
                elif name == "get_repository_files":
                    result = await self.get_repository_files(
                        arguments["owner"],
                        arguments["repo"],
                        arguments.get("path", "")
                    )
                elif name == "get_file_content":
                    result = await self.get_file_content(
                        arguments["owner"],
                        arguments["repo"],
                        arguments["path"],
                        arguments.get("ref", "main")
                    )
                elif name == "create_issue":
                    result = await self.create_issue(
                        arguments["owner"],
                        arguments["repo"],
                        arguments["title"],
                        arguments.get("body", ""),
                        arguments.get("labels", [])
                    )
                elif name == "list_user_repos":
                    result = await self.list_user_repos(
                        arguments.get("type", "all"),
                        arguments.get("sort", "updated"),
                        arguments.get("per_page", 30)
                    )
                else:
                    raise ValueError(f"Unknown tool: {name}")

                return [TextContent(type="text", text=str(result))]
            except Exception as e:
                logger.error(f"Error in tool {name}: {str(e)}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]

    async def make_github_request(self, endpoint: str, method: str = "GET", data: dict = None) -> dict:
        """Make authenticated request to GitHub API"""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHub-MCP-Server/1.0"
        }

        if self.github_token:
            headers["Authorization"] = f"Bearer {self.github_token}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if method == "GET":
                    response = await client.get(f"{self.base_url}{endpoint}", headers=headers)
                elif method == "POST":
                    response = await client.post(
                        f"{self.base_url}{endpoint}",
                        headers=headers,
                        json=data
                    )

                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Request error: {str(e)}")
                raise

    async def get_repositories(self) -> str:
        """Get user's repositories"""
        try:
            repos = await self.make_github_request("/user/repos?per_page=100&sort=updated")
            return json.dumps(repos, indent=2)
        except Exception as e:
            return f"Error fetching repositories: {str(e)}"

    async def get_user_profile(self) -> str:
        """Get user profile"""
        try:
            user = await self.make_github_request("/user")
            return json.dumps(user, indent=2)
        except Exception as e:
            return f"Error fetching user profile: {str(e)}"

    async def get_repository_details(self, owner: str, repo: str) -> str:
        """Get detailed repository information"""
        try:
            repo_data = await self.make_github_request(f"/repos/{owner}/{repo}")
            return json.dumps(repo_data, indent=2)
        except Exception as e:
            return f"Error fetching repository details: {str(e)}"

    async def search_repositories(self, query: str, limit: int = 10) -> str:
        """Search repositories"""
        try:
            # URL encode the query
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            result = await self.make_github_request(
                f"/search/repositories?q={encoded_query}&per_page={min(limit, 100)}&sort=stars&order=desc"
            )
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error searching repositories: {str(e)}"

    async def get_repository_files(self, owner: str, repo: str, path: str = "") -> str:
        """Get repository file structure"""
        try:
            endpoint = f"/repos/{owner}/{repo}/contents"
            if path:
                endpoint += f"/{path.lstrip('/')}"

            contents = await self.make_github_request(endpoint)
            return json.dumps(contents, indent=2)
        except Exception as e:
            return f"Error fetching repository files: {str(e)}"

    async def get_file_content(self, owner: str, repo: str, path: str, ref: str = "main") -> str:
        """Get file content"""
        try:
            endpoint = f"/repos/{owner}/{repo}/contents/{path.lstrip('/')}?ref={ref}"
            content = await self.make_github_request(endpoint)

            if content.get("encoding") == "base64":
                import base64
                try:
                    decoded_content = base64.b64decode(content["content"]).decode("utf-8")
                    return f"File: {path}\nContent:\n{'-' * 50}\n{decoded_content}"
                except UnicodeDecodeError:
                    return f"File: {path}\nNote: Binary file, cannot display content as text.\nSize: {content.get('size', 'unknown')} bytes"

            return json.dumps(content, indent=2)
        except Exception as e:
            return f"Error fetching file content: {str(e)}"

    async def create_issue(self, owner: str, repo: str, title: str, body: str = "", labels: list[str] = None) -> str:
        """Create a new issue"""
        try:
            if not self.github_token:
                return "Error: GitHub token required for creating issues"

            data = {
                "title": title,
                "body": body
            }

            if labels:
                data["labels"] = labels

            issue = await self.make_github_request(
                f"/repos/{owner}/{repo}/issues",
                method="POST",
                data=data
            )
            return json.dumps(issue, indent=2)
        except Exception as e:
            return f"Error creating issue: {str(e)}"

    async def list_user_repos(self, repo_type: str = "all", sort: str = "updated", per_page: int = 30) -> str:
        """List user repositories with filtering options"""
        try:
            params = f"?type={repo_type}&sort={sort}&per_page={min(per_page, 100)}"
            repos = await self.make_github_request(f"/user/repos{params}")
            return json.dumps(repos, indent=2)
        except Exception as e:
            return f"Error listing user repositories: {str(e)}"

    async def run(self):
        """Run the MCP server"""
        # Create server transport using stdio
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="github-mcp-server",
                    server_version="1.0.0",
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )


def main():
    """Main entry point"""
    # Set up environment
    if not os.getenv("GITHUB_TOKEN"):
        print("Warning: GITHUB_TOKEN environment variable not set.")
        print("Some GitHub operations may be limited or fail.")
        print("To set up authentication:")
        print("1. Go to GitHub Settings > Developer settings > Personal access tokens")
        print("2. Generate a new token with 'repo' and 'user' scopes")
        print("3. Set the GITHUB_TOKEN environment variable")

    server = GitHubMCPServer()
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main()