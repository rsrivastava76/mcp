# setup.py
from setuptools import setup, find_packages

setup(
    name="github-mcp-server",
    version="0.1.0",
    description="GitHub MCP Server for Claude Desktop",
    packages=find_packages(),
    install_requires=[
        "httpx>=0.25.0",
        "mcp>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "github-mcp-server=github_mcp_server:main",
        ],
    },
    python_requires=">=3.8",
)
