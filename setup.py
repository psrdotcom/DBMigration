"""Setup script for DBMigration package."""

from setuptools import setup, find_packages

setup(
    name="db-migration",
    version="1.0.0",
    description="Oracle to PostgreSQL migration tool with intelligent agents",
    packages=find_packages(),
    install_requires=[
        "cx_Oracle==8.3.0",
        "psycopg2-binary==2.9.9",
        "python-dotenv==1.0.0",
        "pyyaml==6.0.1",
        "tqdm==4.66.1",
    ],
    extras_require={
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "all": ["openai>=1.0.0", "anthropic>=0.18.0"],
    },
    entry_points={
        "console_scripts": [
            "db-migrate=src.migrate:main",
        ],
    },
    python_requires=">=3.8",
)

