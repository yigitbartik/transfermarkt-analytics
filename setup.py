"""Setup configuration for Transfermarkt Analytics Pro"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="transfermarkt-analytics-pro",
    version="2.0.0",
    author="Analytics Team",
    author_email="info@example.com",
    description="Professional football analytics platform with multi-source data integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/transfermarkt-analytics-pro",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Sports",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "transfermarkt-scrape=run_scraper:run_scraper",
        ],
    },
)
