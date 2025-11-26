#!/usr/bin/env python3
"""
Example usage of the agent system for database migration.

Note: Run this script from the project root directory:
    python scripts/example_usage.py

Or install the package in development mode:
    pip install -e .
"""

from agents.agent_router import AgentRouter
from src.utils.config_loader import load_config


def example_schema_migration():
    """Example: Schema migration using SchemaAgent."""
    config = load_config('config/config.yaml')
    router = AgentRouter(config)
    
    task = {
        'type': 'schema_migration',
        'config': config,
        'tables': None  # Migrate all tables
    }
    
    result = router.execute_task(task)
    print(f"Schema migration result: {result['status']}")
    return result


def example_data_migration():
    """Example: Data migration using DataAgent."""
    config = load_config('config/config.yaml')
    router = AgentRouter(config)
    
    task = {
        'type': 'data_migration',
        'config': config,
        'batch_size': 1000,
        'truncate': False
    }
    
    result = router.execute_task(task)
    print(f"Data migration result: {result['status']}")
    return result


def example_query_conversion():
    """Example: SQL query conversion using QueryAgent."""
    config = load_config('config/config.yaml')
    router = AgentRouter(config)
    
    oracle_query = "SELECT TO_CHAR(created_date, 'YYYY-MM-DD') FROM users WHERE ROWNUM <= 10"
    
    task = {
        'type': 'convert_query',
        'query': oracle_query,
        'config': config
    }
    
    result = router.execute_task(task)
    if result['status'] == 'success':
        print("Original Oracle query:")
        print(result['original_query'])
        print("\nConverted PostgreSQL query:")
        print(result['converted_query'])
    return result


def example_validation():
    """Example: Migration validation using ValidationAgent."""
    config = load_config('config/config.yaml')
    router = AgentRouter(config)
    
    task = {
        'type': 'validate',
        'config': config,
        'schema_sample_size': 10,  # Number of tables to sample for schema validation (default: 10)
        'data_sample_size': 5       # Number of tables to sample for data validation (default: 5)
    }
    
    result = router.execute_task(task)
    print(f"Validation result: {result['status']}")
    return result


def example_list_agents():
    """Example: List all available agents and their capabilities."""
    router = AgentRouter()
    
    print("Available Agents:")
    print("=" * 50)
    capabilities = router.get_agent_capabilities()
    
    for agent_name, caps in capabilities.items():
        print(f"\n{agent_name}:")
        for cap in caps:
            print(f"  - {cap}")


if __name__ == '__main__':
    print("Agent System Examples")
    print("=" * 50)
    
    # List agents
    example_list_agents()
    
    # Uncomment to run examples (requires configured databases):
    # example_schema_migration()
    # example_data_migration()
    # example_query_conversion()
    # example_validation()

