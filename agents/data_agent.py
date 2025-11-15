"""
Data migration agent with LLM assistance for data transformation.
"""

import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, LLMProvider

logger = logging.getLogger(__name__)


class DataAgent(BaseAgent):
    """Agent specialized in data migration tasks."""
    
    def __init__(self, provider: LLMProvider = None, model: str = None):
        # Use GPT-4 for complex data transformations
        super().__init__(
            name="DataAgent",
            provider=provider or LLMProvider.OPENAI,
            model=model or "gpt-4"
        )
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if task is data-related."""
        task_type = task.get('type', '').lower()
        return task_type in ['data', 'data_migration', 'migrate_data', 
                            'transform_data', 'validate_data', 'sync_data']
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute data migration task."""
        task_type = task.get('type', '').lower()
        
        if task_type in ['data', 'data_migration', 'migrate_data']:
            return self._migrate_data(task)
        elif task_type == 'transform_data':
            return self._transform_data(task)
        elif task_type == 'validate_data':
            return self._validate_data(task)
        else:
            return {'status': 'error', 'message': f'Unknown data task: {task_type}'}
    
    def _migrate_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate data using traditional migrator."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.migration.data_migrator import DataMigrator
        from src.utils.config_loader import get_db_connections
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            pg_conn.connect()
            
            try:
                batch_size = task.get('batch_size', 1000)
                data_migrator = DataMigrator(oracle_conn, pg_conn, batch_size=batch_size)
                
                table_filter = task.get('tables')
                truncate = task.get('truncate', False)
                
                results = data_migrator.migrate_all_tables(table_filter, truncate=truncate)
                
                # Use LLM to analyze data quality issues
                failed_tables = [t for t, success in results.items() if not success]
                if failed_tables and self.llm_client:
                    analysis = self._analyze_data_issues(failed_tables, task)
                    return {
                        'status': 'partial_success',
                        'results': results,
                        'failed_tables': failed_tables,
                        'analysis': analysis
                    }
                
                return {
                    'status': 'success',
                    'results': results
                }
            finally:
                oracle_conn.disconnect()
                pg_conn.disconnect()
        
        except Exception as e:
            logger.error(f"Data migration error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _transform_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Transform data using LLM-generated transformation rules."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.utils.config_loader import get_db_connections
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            pg_conn.connect()
            
            try:
                table_name = task.get('table')
                transformation_rules = task.get('rules')
                
                # Use LLM to generate SQL transformation queries
                if self.llm_client and transformation_rules:
                    prompt = f"""
                    Generate PostgreSQL-compatible SQL for data transformation:
                    Table: {table_name}
                    Transformation rules: {transformation_rules}
                    
                    Provide a SQL query that can transform Oracle data format to PostgreSQL format.
                    """
                    
                    sql_query = self.call_llm(
                        prompt,
                        system_prompt="You are a SQL expert specializing in Oracle to PostgreSQL data transformations."
                    )
                    
                    return {
                        'status': 'success',
                        'transformation_sql': sql_query
                    }
                
                return {'status': 'error', 'message': f'Transformation rules required and LLM needed. Please set {self.provider.value.upper()}_API_KEY environment variable.'}
            finally:
                oracle_conn.disconnect()
                pg_conn.disconnect()
        
        except Exception as e:
            logger.error(f"Data transformation error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _validate_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Validate migrated data using LLM-assisted checks."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.utils.config_loader import get_db_connections
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            pg_conn.connect()
            
            try:
                table_name = task.get('table')
                
                # Get row counts
                oracle_count = oracle_conn.get_row_count(table_name)
                pg_count_query = f'SELECT COUNT(*) FROM "{pg_conn.schema}"."{table_name}"'
                pg_result = pg_conn.execute_query(pg_count_query)
                pg_count = pg_result[0]['count'] if pg_result else 0
                
                validation_result = {
                    'table': table_name,
                    'oracle_rows': oracle_count,
                    'postgresql_rows': pg_count,
                    'match': oracle_count == pg_count
                }
                
                # Use LLM to suggest additional validation checks
                if self.llm_client:
                    prompt = f"""
                    Suggest additional data validation checks for migrated table:
                    Table: {table_name}
                    Oracle rows: {oracle_count}
                    PostgreSQL rows: {pg_count}
                    
                    Provide specific SQL queries to validate data integrity.
                    """
                    
                    suggestions = self.call_llm(
                        prompt,
                        system_prompt="You are a data quality expert."
                    )
                    
                    validation_result['llm_suggestions'] = suggestions
                
                return {
                    'status': 'success',
                    'validation': validation_result
                }
            finally:
                oracle_conn.disconnect()
                pg_conn.disconnect()
        
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_data_issues(self, failed_tables: List[str], task: Dict[str, Any]) -> str:
        """Analyze data migration issues using LLM."""
        prompt = f"""
        The following tables failed during data migration:
        {', '.join(failed_tables)}
        
        Analyze potential causes and provide solutions.
        """
        
        return self.call_llm(
            prompt,
            system_prompt="You are an expert in database data migration troubleshooting."
        )
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            'data_migration',
            'data_transformation',
            'data_validation',
            'batch_processing',
            'data_sync'
        ]

