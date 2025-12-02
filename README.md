# Oracle to PostgreSQL Migration Tool

A comprehensive Python tool for migrating databases from Oracle to PostgreSQL, featuring an intelligent agent system that automatically selects the right LLM for each task.

## Features

- **Chatbot UI**: Conversational web interface powered by OpenAI GPT-4.0 for natural language migration control
- **Intelligent Agent System**: Automatically routes tasks to specialized agents with optimal LLM selection
- **Schema Migration**: Converts Oracle schemas to PostgreSQL-compatible schemas
- **Data Migration**: Transfers data with batch processing and progress tracking
- **LLM-Powered Assistance**: Uses GPT-4, Claude, or other LLMs for complex conversions and analysis
- **Multi-Provider Support**: Supports OpenAI, Anthropic, Ollama, and Azure OpenAI
- **Data Type Mapping**: Automatic conversion of Oracle data types to PostgreSQL equivalents
- **Constraint Handling**: Preserves primary keys, foreign keys, and indexes
- **Validation & Quality Assurance**: Comprehensive validation with LLM-assisted analysis

## Project Structure

```
DBMigration/
├── agents/                  # Intelligent agent system
│   ├── __init__.py
│   ├── base_agent.py        # Base agent class with LLM integration
│   ├── agent_router.py      # Task routing and agent selection
│   ├── schema_agent.py      # Schema migration agent
│   ├── data_agent.py        # Data migration agent
│   ├── validation_agent.py  # Validation and QA agent
│   └── query_agent.py       # SQL query conversion agent
├── src/
│   ├── migration/           # Core migration modules
│   │   ├── __init__.py
│   │   ├── db_connector.py
│   │   ├── schema_converter.py
│   │   ├── data_migrator.py
│   │   └── type_mapper.py
│   └── utils/               # Utility modules
│       ├── __init__.py
│       ├── config_loader.py
│       └── natural_language_ui.py
├── config/                  # Configuration files
│   └── config.yaml.example
├── frontend/                # User interface components
│   ├── __init__.py
│   ├── chat_ui.py          # Streamlit chatbot UI (natural language interface)
│   └── nl_ui.py            # Command-line natural language UI
├── tests/                   # Test files
├── scripts/                 # Helper scripts
│   └── example_usage.py
├── migrate.py               # Main migration script
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
└── README.md                # This file
```

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install LLM provider libraries (choose based on your provider):
```bash
# For OpenAI
pip install openai

# For Anthropic Claude
pip install anthropic

# For all providers
pip install openai anthropic
```

3. Install Streamlit (required for Chatbot UI):
```bash
pip install streamlit
```

4. Install Oracle Instant Client (required for cx_Oracle):
   - Download from [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - Follow installation instructions for your platform

5. Install PostgreSQL Client (required for psycopg2):
   - Download from [PostgreSQL Downloads](https://www.postgresql.org/download/)
   - Follow installation instructions for your platform

## Configuration

1. Copy the configuration template:
```bash
cp config/config.yaml.example config/config.yaml
```

2. Edit `config/config.yaml` with your database credentials and LLM settings.

3. Alternatively, use environment variables (see `.env.example` format):
   - `ORACLE_HOST`, `ORACLE_PORT`, `ORACLE_SERVICE_NAME`, etc.
   - `PG_HOST`, `PG_PORT`, `PG_DATABASE`, etc.
   - `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` for LLM features

## Usage

### Interactive Mode (Recommended for First-Time Users)

The interactive mode guides you through the migration process step-by-step, collecting connection details and showing a detailed migration plan before proceeding:

```bash
python migrate.py --interactive
```

**Interactive Workflow:**
1. **Connection Details**: Prompts for Oracle and PostgreSQL connection information
2. **Connection Validation**: Tests both database connections
3. **Schema Discovery**: Lists all available tables in the Oracle schema
4. **Table Selection**: Choose to migrate all tables or select specific ones
5. **Migration Plan**: Displays a detailed plan with:
   - Source and target database information
   - List of tables with row counts and column counts
   - Estimated migration complexity
   - AI-powered insights and recommendations (if LLM is configured)
6. **Approval**: Requires explicit confirmation before starting migration
7. **Execution**: Proceeds with schema and data migration after approval

**Example Interactive Session:**
```
--- Oracle Database Connection ---
Oracle Host [localhost]: db.example.com
Oracle Port [1521]: 1521
Oracle Service Name [ORCL]: PROD
Oracle Username: hr_user
Oracle Password: ****
Oracle Schema (leave empty to use username): HR

--- PostgreSQL Database Connection ---
PostgreSQL Host [localhost]: localhost
PostgreSQL Port [5432]: 5432
PostgreSQL Database: hr_prod
PostgreSQL Username: postgres
PostgreSQL Password: ****
PostgreSQL Schema [public]: public

# Test connection:
# psql -h PG_HOST -U PG_USERNAME -d PG_DATABASE
# sqlplus ORACLE_USERNAME/ORACLE_PASSWORD@ORACLE_HOST:ORACLE_PORT/ORACLE_SERVICE_NAME

✓ All connections validated successfully!

Found 15 tables in schema 'HR':
  EMPLOYEES            DEPARTMENTS          JOBS
  ...

--- Table Selection ---
Options:
  1. Migrate all tables
  2. Select specific tables

Enter your choice [1]: 1

--- MIGRATION PLAN ---
Tables to migrate:     15
Total rows (approx):   125,450
Estimated complexity:  Medium

Do you want to proceed with this migration? (yes/no): yes
```

### Chatbot UI (Natural Language Interface)

The Chatbot UI provides a conversational web interface powered by OpenAI GPT-4.0, allowing you to interact with the migration system using natural language.

**Prerequisites:**
- OpenAI API key configured (set `OPENAI_API_KEY` environment variable)
- OpenAI model set to GPT-4.0 or compatible (set `OPENAI_MODEL` environment variable, defaults to `gpt-4`)
- Configuration file ready (`config/config.yaml` with database credentials)

**Starting the Chatbot:**

```bash
streamlit run frontend/chat_ui.py
```

This will open a web browser with the chatbot interface. If it doesn't open automatically, navigate to `http://localhost:8501`.

**Using the Chatbot:**

1. **Configure Settings** (Sidebar):
   - Set the path to your configuration file (default: `config/config.yaml`)
   - View system information and requirements

2. **Start a Conversation**:
   - Type your migration request in natural language in the chat input
   - Examples:
     - *"Migrate all tables from Oracle to PostgreSQL"*
     - *"Only migrate data for the USERS and ORDERS tables"*
     - *"Validate that the data matches between Oracle and Postgres"*
     - *"Convert this Oracle query to PostgreSQL: SELECT TO_CHAR(date_col) FROM table"*
     - *"Run a full migration with schema and data"*

3. **Review the Plan**:
   - The chatbot will interpret your request and display:
     - **Intent**: What it understood you want to do
     - **Planned Tasks**: List of migration tasks (schema_migration, data_migration, validate, convert_query)
     - **Task Options**: Parameters like table names, batch sizes, truncate flags, etc.
     - **Equivalent CLI Command**: The command-line equivalent for reference

4. **Approve and Execute**:
   - Review the plan carefully
   - Click **"Approve & Run"** to execute the migration tasks
   - Or click **"Cancel Plan"** to discard and start over
   - The chatbot will execute tasks through the AgentRouter and display results

5. **View Results**:
   - After execution, you'll see a summary showing:
     - Which agent handled each task
     - Status of each task (success/error)
     - Any error messages if tasks failed

**Chatbot Features:**

- **Conversational Interface**: Natural language interaction without needing to remember command syntax
- **Plan Preview**: See exactly what will happen before execution
- **Multi-Task Support**: Handles complex requests with multiple tasks (e.g., schema + data migration)
- **Error Handling**: Clear error messages and graceful failure handling
- **Session Management**: Chat history persists during your session

**Example Chat Session:**

```
You: Migrate all tables from Oracle to PostgreSQL

Assistant: I'll help you migrate all tables from Oracle to PostgreSQL.

Intent: Run a full migration (schema and data) from Oracle to PostgreSQL.

Planned tasks:
  1. type = schema_migration
     options:
       - tables: None (all tables)
  2. type = data_migration
     options:
       - tables: None (all tables)
       - truncate: False
       - batch_size: 1000

Equivalent CLI command:
  python migrate.py --config config/config.yaml

[Approve & Run] [Cancel Plan]

---

You: [Clicks Approve & Run]

Assistant: ✓ Executing tasks...

Execution summary:
  1. Agent SchemaAgent -> status: success
  2. Agent DataAgent -> status: success

✓ All planned tasks have been processed.
```

**Tips:**
- Be specific about table names if you only want to migrate certain tables
- Mention "schema only" or "data only" to limit the scope
- Use "validate" or "verify" to check migration quality without making changes
- The chatbot uses GPT-4.0 to interpret your requests, so you can be conversational

### Basic Migration

```bash
python migrate.py --config config/config.yaml
```

### Schema Only

```bash
python migrate.py --config config/config.yaml --schema-only
```

### Data Only (after schema migration)

```bash
python migrate.py --config config/config.yaml --data-only
```

### Specific Tables

```bash
python migrate.py --config config/config.yaml --tables table1,table2
```

### Using Specific Agents

```bash
# Schema migration with schema agent
python migrate.py --config config/config.yaml --task schema_migration

# Data migration with data agent
python migrate.py --config config/config.yaml --task data_migration

# Validation with validation agent
python migrate.py --config config/config.yaml --task validate

# Query conversion with query agent
python migrate.py --config config/config.yaml --query "SELECT * FROM users WHERE id = 1"
```

### List Available Agents

```bash
python migrate.py --list-agents
```

## Agent System

The tool uses an intelligent agent system that automatically selects the right agent and LLM for each task:

### Available Agents

1. **SchemaAgent** (GPT-4)
   - Schema conversion and migration
   - Schema analysis and optimization
   - Table structure conversion

2. **DataAgent** (GPT-4)
   - Data migration and transformation
   - Data validation
   - Batch processing

3. **ValidationAgent** (Claude Opus)
   - Migration validation
   - Database comparison
   - Quality assurance and auditing

4. **QueryAgent** (GPT-4)
   - SQL query conversion
   - Query optimization
   - Query analysis

### LLM Provider Selection

The agent router automatically selects the optimal LLM provider for each task:
- **Schema/Data/Query tasks**: Uses GPT-4 (OpenAI) by default
- **Validation tasks**: Uses Claude Opus (Anthropic) by default
- **Custom providers**: Configure in `config.yaml` under `llm` section

## Configuration File

See `config/config.yaml.example` for configuration options including:
- Source and target database connections
- LLM provider settings
- Table selection filters
- Batch sizes
- Data type mappings
- Custom conversion rules

## Agent Capabilities

Each agent provides specific capabilities:

- **SchemaAgent**: schema_migration, schema_analysis, schema_optimization, table_conversion, constraint_migration
- **DataAgent**: data_migration, data_transformation, data_validation, batch_processing, data_sync
- **ValidationAgent**: migration_validation, data_validation, schema_validation, database_comparison, migration_audit
- **QueryAgent**: query_conversion, sql_translation, query_optimization, query_analysis, syntax_conversion

## Troubleshooting

### Oracle Connection Issues

If you encounter `ORA-12541: Cannot connect. No listener` errors:

1. **Check if Oracle container is running:**
   ```bash
   docker ps | grep oracle
   ```

2. **Run the diagnostic script:**
   ```bash
   ./scripts/check_oracle_connection.sh
   ```

3. **Fix port mapping issues:**
   ```bash
   ./scripts/fix_oracle_connection.sh
   ```

4. **Verify Oracle is ready:**
   ```bash
   docker logs oracle-test | grep "DATABASE IS READY"
   ```

5. **Wait for Oracle to fully start:**
   - Oracle can take 1-2 minutes to fully initialize
   - Monitor progress: `docker logs -f oracle-test`
   - Don't attempt connections until you see "DATABASE IS READY"

6. **Test connection manually:**
   ```bash
   sqlplus testuser/testpass@localhost:1521/XEPDB1
   ```

### Common Issues

- **Port not mapped**: Ensure container was created with `-p 1521:1521`
- **Oracle still starting**: Wait 1-2 minutes after container start
- **Wrong service name**: Use `XEPDB1` for Oracle XE, not `ORCL`
- **Connection timeout**: Check firewall settings and Docker network

## Notes

- Always backup your databases before migration
- Test migrations on a development environment first
- Some Oracle-specific features may require manual conversion
- Large tables are processed in batches to manage memory usage
- LLM features require API keys (set via environment variables or config)
- The tool works without LLM, but LLM features enhance complex conversions

## License

MIT
