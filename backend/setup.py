# -----------------------------------------------------------------------------
# File: setup.py
# Description: Setup configuration for ReqEngine backend package -
#              defines package metadata and dependencies for distribution.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

from setuptools import find_packages, setup

setup(
    name="use-case-extractor-backend",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.11.4",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn==0.24.0",
        "python-multipart==0.0.6",
        "transformers>=4.38.0",
        "sentence-transformers>=2.5.0",
        "accelerate>=0.27.0",
        "huggingface-hub>=0.20.0",
        "nltk==3.8.1",
        "chromadb==0.4.15",
        "PyPDF2==3.0.1",
        "python-docx==1.1.0",
        "pydantic>=2.7.4",
        "python-dateutil==2.8.2",
    ],
    extras_require={
        "dev": [
            "pytest>=8.3.0",
            "pytest-cov>=5.0.0",
            "coverage>=7.3.0",
            "httpx>=0.27.2",
            "pytest-asyncio>=0.23.0",
        ]
    },
)
