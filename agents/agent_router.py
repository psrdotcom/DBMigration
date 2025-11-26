"""
Agent router for intelligent task routing and LLM selection.
"""

import logging
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent, LLMProvider
from .schema_agent import SchemaAgent
from .data_agent import DataAgent
from .validation_agent import ValidationAgent
from .query_agent import QueryAgent

logger = logging.getLogger(__name__)


class AgentRouter:
    """
    Routes tasks to appropriate agents and selects optimal LLM for each task.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.agents: List[BaseAgent] = []
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all available agents."""
        # Get LLM provider preferences from config
        provider_config = self.config.get('llm', {})
        
        # Initialize agents with preferred providers
        self.agents = [
            SchemaAgent(
                provider=self._get_provider(provider_config.get('schema', 'openai')),
                model=provider_config.get('schema_model')
            ),
            DataAgent(
                provider=self._get_provider(provider_config.get('data', 'openai')),
                model=provider_config.get('data_model')
            ),
            ValidationAgent(
                provider=self._get_provider(provider_config.get('validation', 'anthropic')),
                model=provider_config.get('validation_model')
            ),
            QueryAgent(
                provider=self._get_provider(provider_config.get('query', 'openai')),
                model=provider_config.get('query_model')
            ),
        ]
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    def _get_provider(self, provider_str: str) -> LLMProvider:
        """Convert string to LLMProvider enum."""
        try:
            return LLMProvider(provider_str.lower())
        except (ValueError, AttributeError):
            return LLMProvider.OPENAI
    
    def route_task(self, task: Dict[str, Any]) -> Optional[BaseAgent]:
        """
        Route a task to the most appropriate agent.
        
        Args:
            task: Task dictionary with 'type' and other parameters
            
        Returns:
            Agent that can handle the task, or None if no agent found
        """
        # First, try to find agent that explicitly can handle the task
        for agent in self.agents:
            if agent.can_handle(task):
                logger.info(f"Routing task '{task.get('type')}' to {agent.name}")
                return agent
        
        # If no direct match, use LLM to determine best agent
        task_type = task.get('type', '').lower()
        task_description = task.get('description', '')
        
        # Use the first available agent's LLM to help route
        if self.agents and self.agents[0].llm_client:
            best_agent = self._llm_route_task(task_type, task_description)
            if best_agent:
                logger.info(f"LLM routed task '{task_type}' to {best_agent.name}")
                return best_agent
        
        # Fallback: return first agent if task type is generic
        if task_type in ['migrate', 'migration']:
            logger.warning(f"No specific agent for '{task_type}', using SchemaAgent")
            return self.agents[0] if self.agents else None
        
        logger.warning(f"No agent found for task type: {task_type}")
        return None
    
    def _llm_route_task(self, task_type: str, description: str) -> Optional[BaseAgent]:
        """Use LLM to intelligently route task to best agent."""
        agent_descriptions = {
            'SchemaAgent': 'Handles schema conversion, table creation, schema analysis, and optimization',
            'DataAgent': 'Handles data migration, transformation, validation, and synchronization',
            'ValidationAgent': 'Handles validation, verification, comparison, and auditing',
            'QueryAgent': 'Handles SQL query conversion, translation, optimization, and analysis'
        }
        
        prompt = f"""
        Task type: {task_type}
        Description: {description}
        
        Available agents:
        {chr(10).join([f"- {name}: {desc}" for name, desc in agent_descriptions.items()])}
        
        Which agent should handle this task? Respond with only the agent name.
        """
        
        # Use first agent's LLM (they all have same interface)
        response = self.agents[0].call_llm(
            prompt,
            system_prompt="You are a task routing expert. Select the most appropriate agent for each task.",
            temperature=0.1,
            max_tokens=50
        )
        
        if response:
            agent_name = response.strip()
            for agent in self.agents:
                if agent.name == agent_name:
                    return agent
        
        return None
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route and execute a task.
        
        Args:
            task: Task dictionary
            
        Returns:
            Task execution result
        """
        agent = self.route_task(task)
        
        if not agent:
            return {
                'status': 'error',
                'message': f"No agent found for task type: {task.get('type')}"
            }
        
        try:
            result = agent.execute(task)
            result['agent'] = agent.name
            return result
        except Exception as e:
            logger.error(f"Error executing task with {agent.name}: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'agent': agent.name
            }
    
    def get_agent_capabilities(self) -> Dict[str, List[str]]:
        """Get capabilities of all agents."""
        return {
            agent.name: agent.get_capabilities()
            for agent in self.agents
        }
    
    def list_agents(self) -> List[str]:
        """List all available agent names."""
        return [agent.name for agent in self.agents]

