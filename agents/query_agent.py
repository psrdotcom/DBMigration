"""
Query conversion agent for SQL query translation.
"""

import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent, LLMProvider

logger = logging.getLogger(__name__)


class QueryAgent(BaseAgent):
    """Agent specialized in SQL query conversion."""
    
    def __init__(self, provider: LLMProvider = None, model: str = None):
        # Use GPT-4 for SQL translation
        super().__init__(
            name="QueryAgent",
            provider=provider or LLMProvider.OPENAI,
            model=model or "gpt-4"
        )
    
    def can_handle(self, task: Dict[str, Any]) -> bool:
        """Check if task is query-related."""
        task_type = task.get('type', '').lower()
        return task_type in ['query', 'convert_query', 'translate_query', 
                            'optimize_query', 'analyze_query']
    
    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query conversion task."""
        task_type = task.get('type', '').lower()
        
        if task_type in ['query', 'convert_query', 'translate_query']:
            return self._convert_query(task)
        elif task_type == 'optimize_query':
            return self._optimize_query(task)
        elif task_type == 'analyze_query':
            return self._analyze_query(task)
        else:
            return {'status': 'error', 'message': f'Unknown query task: {task_type}'}
    
    def _convert_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Oracle SQL to PostgreSQL SQL."""
        oracle_query = task.get('query')
        if not oracle_query or not isinstance(oracle_query, str):
            return {'status': 'error', 'message': 'Valid query string required'}
        if not oracle_query.strip():
            return {'status': 'error', 'message': 'Query cannot be empty'}
        
        if self.llm_client:
            prompt = f"""
            Convert this Oracle SQL query to PostgreSQL-compatible SQL:
            
            {oracle_query}
            
            Requirements:
            1. Maintain the same logic and results
            2. Use PostgreSQL syntax
            3. Handle Oracle-specific functions appropriately
            4. Preserve query structure
            5. Add comments explaining any significant changes
            """
            
            converted_query = self.call_llm(
                prompt,
                system_prompt="You are an expert SQL translator specializing in Oracle to PostgreSQL conversion."
            )
            
            return {
                'status': 'success',
                'original_query': oracle_query,
                'converted_query': converted_query
            }
        
        return {'status': 'error', 'message': f'LLM required for query conversion. Please set {self.provider.value.upper()}_API_KEY environment variable.'}
    
    def _optimize_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize PostgreSQL query."""
        query = task.get('query')
        if not query:
            return {'status': 'error', 'message': 'Query required'}
        
        if self.llm_client:
            prompt = f"""
            Optimize this PostgreSQL query for better performance:
            
            {query}
            
            Provide:
            1. Optimized query
            2. Explanation of optimizations
            3. Index recommendations
            """
            
            optimization = self.call_llm(
                prompt,
                system_prompt="You are a PostgreSQL query optimization expert."
            )
            
            return {
                'status': 'success',
                'original_query': query,
                'optimization': optimization
            }
        
        return {'status': 'error', 'message': f'LLM required for query optimization. Please set {self.provider.value.upper()}_API_KEY environment variable.'}
    
    def _analyze_query(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze query for migration compatibility."""
        query = task.get('query')
        if not query:
            return {'status': 'error', 'message': 'Query required'}
        
        if self.llm_client:
            prompt = f"""
            Analyze this SQL query for Oracle to PostgreSQL migration:
            
            {query}
            
            Identify:
            1. Oracle-specific features
            2. Potential conversion issues
            3. Compatibility concerns
            4. Recommended changes
            """
            
            analysis = self.call_llm(
                prompt,
                system_prompt="You are a database migration compatibility expert."
            )
            
            return {
                'status': 'success',
                'query': query,
                'analysis': analysis
            }
        
        return {'status': 'error', 'message': f'LLM required for query analysis. Please set {self.provider.value.upper()}_API_KEY environment variable.'}
    
    def get_capabilities(self) -> List[str]:
        """Get agent capabilities."""
        return [
            'query_conversion',
            'sql_translation',
            'query_optimization',
            'query_analysis',
            'syntax_conversion'
        ]

