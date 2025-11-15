# Agent System Documentation

## Overview

The DBMigration tool uses an intelligent agent system that automatically routes tasks to specialized agents, each optimized with the right LLM for their specific domain.

## Architecture

```
User Request
    ↓
AgentRouter (Task Router)
    ↓
[SchemaAgent | DataAgent | ValidationAgent | QueryAgent]
    ↓
BaseAgent (LLM Integration)
    ↓
[OpenAI GPT-4 | Anthropic Claude | Ollama | Azure OpenAI]
```

## Agent Selection

The `AgentRouter` intelligently selects the best agent for each task:

1. **Direct Matching**: Checks if any agent explicitly handles the task type
2. **LLM Routing**: Uses LLM to determine the best agent if no direct match
3. **Fallback**: Uses default agent for generic migration tasks

## Available Agents

### 1. SchemaAgent

**Purpose**: Handles all schema-related migration tasks

**LLM Provider**: OpenAI GPT-4 (default)

**Capabilities**:
- Schema migration and conversion
- Schema analysis and complexity assessment
- Schema optimization recommendations
- Table structure conversion
- Constraint migration

**Task Types**:
- `schema_migration` / `schema` / `convert_schema`
- `analyze_schema`
- `optimize_schema`
- `create_table`

**Example**:
```python
task = {
    'type': 'schema_migration',
    'config': config,
    'tables': ['users', 'orders']
}
result = router.execute_task(task)
```

### 2. DataAgent

**Purpose**: Handles data migration and transformation

**LLM Provider**: OpenAI GPT-4 (default)

**Capabilities**:
- Data migration with batch processing
- Data transformation rules
- Data validation
- Data synchronization
- Error analysis and recovery

**Task Types**:
- `data_migration` / `data` / `migrate_data`
- `transform_data`
- `validate_data`
- `sync_data`

**Example**:
```python
task = {
    'type': 'data_migration',
    'config': config,
    'batch_size': 1000,
    'truncate': False
}
result = router.execute_task(task)
```

### 3. ValidationAgent

**Purpose**: Quality assurance and validation

**LLM Provider**: Anthropic Claude Opus (default)

**Capabilities**:
- Comprehensive migration validation
- Database comparison
- Data integrity checks
- Migration auditing
- Quality assurance reports

**Task Types**:
- `validate` / `validation` / `verify`
- `compare`
- `audit`
- `quality_check`

**Example**:
```python
task = {
    'type': 'validate',
    'config': config
}
result = router.execute_task(task)
```

### 4. QueryAgent

**Purpose**: SQL query conversion and optimization

**LLM Provider**: OpenAI GPT-4 (default)

**Capabilities**:
- Oracle to PostgreSQL query conversion
- SQL query optimization
- Query analysis and compatibility checking
- Syntax translation
- Performance recommendations

**Task Types**:
- `convert_query` / `query` / `translate_query`
- `optimize_query`
- `analyze_query`

**Example**:
```python
task = {
    'type': 'convert_query',
    'query': 'SELECT TO_CHAR(date_col) FROM table',
    'config': config
}
result = router.execute_task(task)
```

## LLM Provider Configuration

### Supported Providers

1. **OpenAI** (`openai`)
   - Models: gpt-4, gpt-3.5-turbo, etc.
   - Environment: `OPENAI_API_KEY`

2. **Anthropic** (`anthropic`)
   - Models: claude-3-opus-20240229, claude-3-sonnet, etc.
   - Environment: `ANTHROPIC_API_KEY`

3. **Ollama** (`ollama`)
   - Models: llama2, mistral, etc.
   - Environment: `OLLAMA_BASE_URL` (default: http://localhost:11434/v1)

4. **Azure OpenAI** (`azure_openai`)
   - Models: gpt-4, gpt-35-turbo
   - Environment: `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_VERSION`

### Configuration

Configure LLM providers in `config/config.yaml`:

```yaml
llm:
  schema: openai          # Provider for schema tasks
  schema_model: gpt-4     # Model name
  data: openai
  data_model: gpt-4
  validation: anthropic
  validation_model: claude-3-opus-20240229
  query: openai
  query_model: gpt-4
```

Or via environment variables:
```bash
export LLM_PROVIDER=openai
export OPENAI_API_KEY=your_key_here
```

## Custom Agent Development

To create a custom agent:

1. Inherit from `BaseAgent`:
```python
from agents.base_agent import BaseAgent, LLMProvider

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="CustomAgent",
            provider=LLMProvider.OPENAI,
            model="gpt-4"
        )
    
    def can_handle(self, task):
        return task.get('type') == 'custom_task'
    
    def execute(self, task):
        # Your implementation
        return {'status': 'success'}
```

2. Register in `AgentRouter`:
```python
# In agent_router.py
from .custom_agent import CustomAgent

self.agents.append(CustomAgent())
```

## Best Practices

1. **Task Type Naming**: Use descriptive, specific task types
2. **Error Handling**: Always return structured results with status
3. **LLM Usage**: Use LLM for complex analysis, not simple operations
4. **Fallback**: Ensure agents work without LLM (graceful degradation)
5. **Logging**: Log all agent actions for debugging

## Performance Considerations

- LLM calls add latency; use for complex tasks only
- Batch operations when possible
- Cache LLM responses for repeated queries
- Use appropriate model sizes (smaller models for simple tasks)

