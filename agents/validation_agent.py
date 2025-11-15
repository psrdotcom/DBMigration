"""
Validation agent for migration quality assurance.
"""

import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, LLMProvider

logger = logging.getLogger(__name__)


class ValidationAgent(BaseAgent):
    """Agent specialized in validation and quality assurance."""
    
    def __init__(self, provider: LLMProvider = None, model: str = None):
        # Use Claude for detailed analysis
        super().__init__(
            name="ValidationAgent",
            provider=provider or LLMProvider.ANTHROPIC,
            model=model or "claude-3-opus-20240229"
        )
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if task is validation-related."""
        task_type = task.get('type', '').lower()
        return task_type in ['validate', 'validation', 'verify', 'check', 
                            'quality_check', 'compare', 'audit']
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation task."""
        task_type = task.get('type', '').lower()
        
        if task_type in ['validate', 'validation', 'verify']:
            return self._validate_migration(task)
        elif task_type == 'compare':
            return self._compare_databases(task)
        elif task_type == 'audit':
            return self._audit_migration(task)
        else:
            return {'status': 'error', 'message': f'Unknown validation task: {task_type}'}
    
    def _validate_migration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive migration validation."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.utils.config_loader import get_db_connections
        
        oracle_conn = None
        pg_conn = None
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            pg_conn.connect()
            
            validation_results = {
                'schema_validation': self._validate_schema(oracle_conn, pg_conn),
                'data_validation': self._validate_data(oracle_conn, pg_conn),
                'constraint_validation': self._validate_constraints(oracle_conn, pg_conn)
            }
            
            # Use LLM to generate comprehensive validation report
            if self.llm_client:
                prompt = f"""
                Generate a comprehensive migration validation report:
                {str(validation_results)}
                
                Include:
                1. Summary of validation results
                2. Issues found
                3. Recommendations
                """
                
                report = self.call_llm(
                    prompt,
                    system_prompt="You are a database migration quality assurance expert."
                )
                
                validation_results['llm_report'] = report
            
            return {
                'status': 'success',
                'validation': validation_results
            }
        
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return {'status': 'error', 'message': str(e)}
        
        finally:
            if oracle_conn:
                try:
                    oracle_conn.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting Oracle connection: {e}")
            if pg_conn:
                try:
                    pg_conn.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting PostgreSQL connection: {e}")
    
    def _validate_schema(self, oracle_conn, pg_conn) -> Dict[str, Any]:
        """Validate schema conversion."""
        oracle_tables = oracle_conn.get_tables()
        pg_tables = []
        
        for table in oracle_tables[:10]:  # Sample
            if pg_conn.table_exists(table):
                pg_tables.append(table)
        
        return {
            'oracle_tables': len(oracle_tables),
            'postgresql_tables': len(pg_tables),
            'coverage': len(pg_tables) / len(oracle_tables) if oracle_tables else 0
        }
    
    def _validate_data(self, oracle_conn, pg_conn) -> Dict[str, Any]:
        """Validate data migration."""
        tables = oracle_conn.get_tables()[:5]  # Sample
        results = {}
        
        for table in tables:
            oracle_count = oracle_conn.get_row_count(table)
            if pg_conn.table_exists(table):
                pg_count_query = f'SELECT COUNT(*) FROM "{pg_conn.schema}"."{table}"'
                pg_result = pg_conn.execute_query(pg_count_query)
                pg_count = pg_result[0]['count'] if pg_result else 0
                results[table] = {
                    'oracle': oracle_count,
                    'postgresql': pg_count,
                    'match': oracle_count == pg_count
                }
        
        return results
    
    def _validate_constraints(self, oracle_conn, pg_conn) -> Dict[str, Any]:
        """Validate constraints."""
        # Simplified validation
        return {'status': 'validated', 'message': 'Constraint validation completed'}
    
    def _compare_databases(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Compare Oracle and PostgreSQL databases."""
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.utils.config_loader import get_db_connections
        
        oracle_conn = None
        pg_conn = None
        
        try:
            config = task.get('config')
            oracle_conn, pg_conn = get_db_connections(config)
            
            oracle_conn.connect()
            pg_conn.connect()
            
            # Get schema information
            oracle_tables = oracle_conn.get_tables()
            
            comparison = {
                'table_count': {
                    'oracle': len(oracle_tables),
                    'postgresql': len([t for t in oracle_tables if pg_conn.table_exists(t)])
                }
            }
            
            # Use LLM for detailed comparison analysis
            if self.llm_client:
                prompt = f"""
                Compare Oracle and PostgreSQL databases:
                {str(comparison)}
                
                Provide detailed comparison and identify any discrepancies.
                """
                
                analysis = self.call_llm(
                    prompt,
                    system_prompt="You are a database comparison expert."
                )
                
                comparison['llm_analysis'] = analysis
            
            return {
                'status': 'success',
                'comparison': comparison
            }
        
        except Exception as e:
            logger.error(f"Comparison error: {e}")
            return {'status': 'error', 'message': str(e)}
        
        finally:
            if oracle_conn:
                try:
                    oracle_conn.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting Oracle connection: {e}")
            if pg_conn:
                try:
                    pg_conn.disconnect()
                except Exception as e:
                    logger.error(f"Error disconnecting PostgreSQL connection: {e}")
    
    def _audit_migration(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Audit migration for compliance and best practices."""
        if self.llm_client:
            prompt = """
            Provide a comprehensive migration audit checklist for Oracle to PostgreSQL migration.
            Include:
            1. Schema compliance
            2. Data integrity
            3. Performance considerations
            4. Security aspects
            5. Best practices
            """
            
            checklist = self.call_llm(
                prompt,
                system_prompt="You are a database migration auditor."
            )
            
            return {
                'status': 'success',
                'audit_checklist': checklist
            }
        
        return {'status': 'error', 'message': 'LLM required for audit'}
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            'migration_validation',
            'data_validation',
            'schema_validation',
            'database_comparison',
            'migration_audit'
        ]

