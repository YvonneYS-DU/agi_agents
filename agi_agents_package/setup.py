"""
Setup script for AGI Agents package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="agi-agents",
    version="0.2.1",
    author="YvonneYS-Du",
    author_email="yvdu.ai2077@gmail.com",
    description="A streamlined interface for LangChain AI Agent creation with multi-modal support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/YvonneYS-DU/agi_agents",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.10",
    install_requires=[
        # LangChain ecosystem - upgraded to 1.0+
        "langchain>=1.0.0",
        "langchain-core>=1.0.0",
        "langchain-openai>=1.0.0",
        "langchain-anthropic>=1.0.0",
        "langchain-google-genai>=4.0.0",
        "langchain-text-splitters>=1.0.0",

        # AI API clients
        "openai>=1.76.0",
        "anthropic>=0.40.0",

        # HTTP clients
        "httpx>=0.27.2",
        "aiohttp>=3.8.0",
        "aiofiles>=23.0.0",
        
        # Document processing
        "PyMuPDF>=1.20.0",
        "python-docx>=1.0.0",
        "unstructured>=0.15.0",
        "openpyxl>=3.1.0",
        
        # Image processing
        "Pillow>=9.0.0",
        "pillow-heif>=0.8.0",
        
        # Data processing
        "pandas>=1.5.0",
        "regex>=2020.1.1",
        
        # Azure support
        "azure-storage-blob>=12.0.0",
        
        # Utilities
        "python-dotenv>=1.0.0",
        "urllib3>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    keywords="langchain, ai, llm, multimodal, agents, wrapper",
    project_urls={
        "Bug Reports": "https://github.com/YvonneYS-DU/agi_agents/issues",
        "Source": "https://github.com/YvonneYS-DU/agi_agents",
    },
)