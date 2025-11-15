"""
Schema migration agent with LLM assistance for complex conversions.
"""

import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, LLMProvider

logger = logging.getLogger(__name__)


class SchemaAgent(BaseAgent):
    """Agent specialized in schema migration tasks."""
    
    def __init__(self, provider: LLMProvider = None, model: str = None):
        # Use GPT-4 or Claude for complex schema analysis
        super().__init__(
            name="SchemaAgent",
            provider=provider or LLMProvider.OPENAI,
            model=model or "gpt-4"
        )
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if task is schema-related."""
        task_type = task.get('type', '').lower()
        return task_type in ['schema', 'schema_migration', 'convert_schema', 
                            'create_table', 'analyze_schema', 'optimize_schema']
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute schema migration task."""
        task_type = task.get('type', '').lower()
        
        if task_type in ['schema', 'schema_migration', 'convert_schema']:
            return self._migrate_schema(task)
        elif task_type == 'analyze_schema':
            return self._analyze_schema(task)
        elif task_type == 'optimize_schema':
            return self._optimize_schema(task)
        else:
            return {'status': 'error', 'message': f'Unknown schema task: {task_type}'}
    
    def _migrate_schema(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate schema using traditional converter with LLM assistance for edge cases."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.migration.schema_converter import SchemaConverter
        from src.utils.config_loader import get_db_connections
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            pg_conn.connect()
            
            try:
                schema_converter = SchemaConverter(oracle_conn, pg_conn)
                table_filter = task.get('tables')
                
                results = schema_converter.convert_all_tables(table_filter)
                
                # Use LLM to analyze and suggest improvements for failed conversions
                failed_tables = [t for t, success in results.items() if not success]
                if failed_tables and self.llm_client:
                    suggestions = self._get_llm_suggestions(failed_tables, task)
                    return {
                        'status': 'partial_success',
                        'results': results,
                        'failed_tables': failed_tables,
                        'suggestions': suggestions
                    }
                
                return {
                    'status': 'success',
                    'results': results
                }
            finally:
                oracle_conn.disconnect()
                pg_conn.disconnect()
        
        except Exception as e:
            logger.error(f"Schema migration error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _analyze_schema(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Oracle schema and provide insights using LLM."""
        from src.utils.config_loader import get_db_connections
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            
            try:
                tables = oracle_conn.get_tables()
                schema_info = {
                    'table_count': len(tables),
                    'tables': tables[:10]  # Sample
                }
                
                # Use LLM to analyze schema complexity
                if self.llm_client:
                    prompt = f"""
                    Analyze this Oracle database schema:
                    - Number of tables: {len(tables)}
                    - Sample tables: {', '.join(tables[:10])}
                    
                    Provide insights on:
                    1. Migration complexity
                    2. Potential challenges
                    3. Recommended approach
                    """
                    
                    analysis = self.call_llm(
                        prompt,
                        system_prompt="You are a database migration expert specializing in Oracle to PostgreSQL migrations."
                    )
                    
                    return {
                        'status': 'success',
                        'schema_info': schema_info,
                        'llm_analysis': analysis
                    }
                
                return {
                    'status': 'success',
                    'schema_info': schema_info
                }
            finally:
                oracle_conn.disconnect()
        
        except Exception as e:
            logger.error(f"Schema analysis error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _optimize_schema(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize PostgreSQL schema using LLM suggestions."""
        from src.utils.config_loader import get_db_connections
        
        try:
            config = task.get('config')
            _, pg_conn = get_db_connections(config)
            
            pg_conn.connect()
            
            try:
                # Get current schema
                query = """
                    SELECT table_name, column_name, data_type
                    FROM information_schema.columns
                    WHERE table_schema = %s
                    LIMIT 50
                """
                columns = pg_conn.execute_query(query, (pg_conn.schema,))
                
                if self.llm_client:
                    prompt = f"""
                    Analyze this PostgreSQL schema and suggest optimizations:
                    {str(columns[:20])}
                    
                    Consider:
                    1. Index recommendations
                    2. Data type optimizations
                    3. Constraint improvements
                    """
                    
                    suggestions = self.call_llm(
                        prompt,
                        system_prompt="You are a PostgreSQL performance optimization expert."
                    )
                    
                    return {
                        'status': 'success',
                        'suggestions': suggestions
                    }
                
                return {'status': 'success', 'message': f'Schema optimization requires LLM. Please set {self.provider.value.upper()}_API_KEY environment variable.'}
            finally:
                pg_conn.disconnect()
        
        except Exception as e:
            logger.error(f"Schema optimization error: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _get_llm_suggestions(self, failed_tables: List[str], task: Dict[str, Any]) -> str:
        """Get LLM suggestions for failed table conversions."""
        prompt = f"""
        The following Oracle tables failed to convert to PostgreSQL:
        {', '.join(failed_tables)}
        
        Provide specific suggestions for resolving these conversion issues.
        """
        
        return self.call_llm(
            prompt,
            system_prompt="You are an expert in Oracle to PostgreSQL database migration."
        )
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            'schema_migration',
            'schema_analysis',
            'schema_optimization',
            'table_conversion',
            'constraint_migration'
        ]

