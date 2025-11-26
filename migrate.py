#!/usr/bin/env python3
"""
Main migration script for Oracle to PostgreSQL migration with agent system.
"""

import argparse
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv

from agents.agent_router import AgentRouter
from src.utils.config_loader import load_config

# Initialize Oracle Client for macOS
try:
    import cx_Oracle
    import platform
    if platform.system() == "Darwin":
        lib_dir = "~/oracle/instantclient_23_3"
        cx_Oracle.init_oracle_client(lib_dir=lib_dir)
except Exception:
    pass  # Ignore if cx_Oracle is not installed or already initialized

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('migration.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(
        description='Migrate database from Oracle to PostgreSQL using intelligent agents'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )
    parser.add_argument(
        '--task',
        type=str,
        help='Specific task type (schema, data, validate, query, etc.)'
    )
    parser.add_argument(
        '--schema-only',
        action='store_true',
        help='Only migrate schema, skip data'
    )
    parser.add_argument(
        '--data-only',
        action='store_true',
        help='Only migrate data, skip schema (assumes schema already exists)'
    )
    parser.add_argument(
        '--tables',
        type=str,
        help='Comma-separated list of specific tables to migrate'
    )
    parser.add_argument(
        '--truncate',
        action='store_true',
        help='Truncate target tables before data migration'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1000,
        help='Batch size for data migration (default: 1000)'
    )
    parser.add_argument(
        '--list-agents',
        action='store_true',
        help='List all available agents and their capabilities'
    )
    parser.add_argument(
        '--query',
        type=str,
        help='SQL query to convert (for query agent)'
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Run in interactive mode (prompts for connection details and shows migration plan)'
    )

    
    args = parser.parse_args()
    
    try:
        # Handle interactive mode first
        if args.interactive:
            from src.utils.interactive_planner import run_interactive_mode
            
            logger.info("Starting interactive migration mode")
            config, selected_tables = run_interactive_mode()
            
            if config is None:
                logger.info("Interactive mode cancelled or failed")
                return 1
            
            # Initialize agent router with the generated config
            router = AgentRouter(config)
            
            # Execute migration tasks
            tasks = []
            
            if not args.data_only:
                tasks.append({
                    'type': 'schema_migration',
                    'config': config,
                    'tables': selected_tables
                })
            
            if not args.schema_only:
                tasks.append({
                    'type': 'data_migration',
                    'config': config,
                    'tables': selected_tables,
                    'truncate': args.truncate,
                    'batch_size': args.batch_size
                })
            
            # Execute tasks
            all_results = []
            for task in tasks:
                logger.info(f"Executing task: {task['type']}")
                result = router.execute_task(task)
                all_results.append(result)
                
                if result.get('status') == 'error':
                    logger.error(f"Task {task['type']} failed: {result.get('message')}")
                    return 1
            
            # Summary
            logger.info("=" * 50)
            logger.info("Migration Summary:")
            for result in all_results:
                logger.info(f"  {result.get('agent', 'Unknown')}: {result.get('status', 'unknown')}")
            
            logger.info("Migration completed successfully!")
            return 0
        
        # List agents if requested (before loading config)
        if args.list_agents:

            router = AgentRouter()
            print("\nAvailable Agents:")
            print("=" * 50)
            capabilities = router.get_agent_capabilities()
            for agent_name, caps in capabilities.items():
                print(f"\n{agent_name}:")
                for cap in caps:
                    print(f"  - {cap}")
            return 0
        
        # Load configuration for other operations
        logger.info(f"Loading configuration from {args.config}")
        config = load_config(args.config)
        
        # Initialize agent router
        router = AgentRouter(config)
        
        # Handle query conversion
        if args.query:
            task = {
                'type': 'convert_query',
                'query': args.query,
                'config': config
            }
            logger.info(f"Executing task: {task.get('type')}")
            result = router.execute_task(task)
            
            if result.get('status') == 'error':
                logger.error(f"Task failed: {result.get('message')}")
                return 1
            
            logger.info("Task completed successfully!")
            return 0
        
        # Handle specific task type
        if args.task:
            task = {
                'type': args.task,
                'config': config,
                'tables': [t.strip() for t in args.tables.split(',')] if args.tables else None,
                'truncate': args.truncate,
                'batch_size': args.batch_size
            }
            logger.info(f"Executing task: {task.get('type')}")
            result = router.execute_task(task)
            
            if result.get('status') == 'error':
                logger.error(f"Task failed: {result.get('message')}")
                return 1
            
            logger.info("Task completed successfully!")
            return 0
        
        # Default migration task
        tasks = []
        
        if not args.data_only:
            tasks.append({
                'type': 'schema_migration',
                'config': config,
                'tables': [t.strip() for t in args.tables.split(',')] if args.tables else None
            })
        
        if not args.schema_only:
            tasks.append({
                'type': 'data_migration',
                'config': config,
                'tables': [t.strip() for t in args.tables.split(',')] if args.tables else None,
                'truncate': args.truncate,
                'batch_size': args.batch_size
            })
        
        # Execute tasks
        all_results = []
        for task in tasks:
            logger.info(f"Executing task: {task['type']}")
            result = router.execute_task(task)
            all_results.append(result)
            
            if result.get('status') == 'error':
                logger.error(f"Task {task['type']} failed: {result.get('message')}")
                return 1
        
        # Summary
        logger.info("=" * 50)
        logger.info("Migration Summary:")
        for result in all_results:
            logger.info(f"  {result.get('agent', 'Unknown')}: {result.get('status', 'unknown')}")
        
        logger.info("Migration completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Migration failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
