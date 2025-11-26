# Oracle to PostgreSQL Migration Tool

A comprehensive Python tool for migrating databases from Oracle to PostgreSQL, featuring an intelligent agent system that automatically selects the right LLM for each task.

## Features

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
│   ├── base_agent.py       # Base agent class with LLM integration
│   ├── agent_router.py     # Task routing and agent selection
│   ├── schema_agent.py     # Schema migration agent
│   ├── data_agent.py       # Data migration agent
│   ├── validation_agent.py # Validation and QA agent
│   └── query_agent.py      # SQL query conversion agent
├── src/
│   ├── migration/          # Core migration modules
│   │   ├── __init__.py
│   │   ├── db_connector.py
│   │   ├── schema_converter.py
│   │   ├── data_migrator.py
│   │   └── type_mapper.py
│   └── utils/              # Utility modules
│       ├── __init__.py
│       └── config_loader.py
├── config/                 # Configuration files
│   └── config.yaml.example
├── tests/                  # Test files
├── scripts/                # Helper scripts
├── migrate.py             # Main migration script
├── requirements.txt       # Python dependencies
├── setup.py               # Package setup
└── README.md              # This file
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

3. Install Oracle Instant Client (required for cx_Oracle):
   - Download from [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
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

## Notes

- Always backup your databases before migration
- Test migrations on a development environment first
- Some Oracle-specific features may require manual conversion
- Large tables are processed in batches to manage memory usage
- LLM features require API keys (set via environment variables or config)
- The tool works without LLM, but LLM features enhance complex conversions

## License

MIT
