# Oracle to PostgreSQL Migration Tool

A comprehensive Python tool for migrating databases from Oracle to PostgreSQL, including schema conversion and data migration.

## Features

- **Schema Migration**: Converts Oracle schemas to PostgreSQL-compatible schemas
- **Data Migration**: Transfers data with batch processing and progress tracking
- **Data Type Mapping**: Automatic conversion of Oracle data types to PostgreSQL equivalents
- **Constraint Handling**: Preserves primary keys, foreign keys, and indexes
- **Error Handling**: Robust error handling with detailed logging

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Oracle Instant Client (required for cx_Oracle):
   - Download from [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
   - Follow installation instructions for your platform

## Configuration

1. Copy `.env.example` to `.env` and fill in your database credentials:
```bash
cp .env.example .env
```

2. Edit `.env` with your Oracle and PostgreSQL connection details.

## Usage

### Basic Migration

```bash
python migrate.py --config config.yaml
```

### Schema Only

```bash
python migrate.py --config config.yaml --schema-only
```

### Data Only (after schema migration)

```bash
python migrate.py --config config.yaml --data-only
```

### Specific Tables

```bash
python migrate.py --config config.yaml --tables table1,table2
```

## Configuration File

See `config.yaml.example` for configuration options including:
- Source and target database connections
- Table selection filters
- Batch sizes
- Data type mappings
- Custom conversion rules

## Project Structure

```
DBMigration/
├── migrate.py              # Main migration script
├── schema_converter.py     # Schema conversion utilities
├── data_migrator.py       # Data migration utilities
├── db_connector.py        # Database connection handlers
├── type_mapper.py         # Data type mapping functions
├── config.yaml.example    # Configuration template
├── .env.example           # Environment variables template
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Notes

- Always backup your databases before migration
- Test migrations on a development environment first
- Some Oracle-specific features may require manual conversion
- Large tables are processed in batches to manage memory usage

## License

MIT

