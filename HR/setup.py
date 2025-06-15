# setup.py - Optional setup script for packaging
from setuptools import setup, find_packages

setup(
    name="hr-management-mcp-server",
    version="1.0.0",
    description="MCP Server for HR Management System with MySQL support",
    author="Ritesh Srivastava",
    author_email="rsrivastava76@hotmail.com",
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "mysql-connector-python>=8.0.33",
        "python-dotenv>=1.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "hr-mcp-server=hr_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)