"""
Data type mapping from Oracle to PostgreSQL.
"""

import logging

logger = logging.getLogger(__name__)


class TypeMapper:
    """Maps Oracle data types to PostgreSQL equivalents."""
    
    # Oracle to PostgreSQL type mapping
    TYPE_MAPPING = {
        'VARCHAR2': 'VARCHAR',
        'NVARCHAR2': 'VARCHAR',
        'CHAR': 'CHAR',
        'NCHAR': 'CHAR',
        'NUMBER': 'NUMERIC',
        'FLOAT': 'DOUBLE PRECISION',
        'BINARY_FLOAT': 'REAL',
        'BINARY_DOUBLE': 'DOUBLE PRECISION',
        'DATE': 'TIMESTAMP',
        'TIMESTAMP': 'TIMESTAMP',
        'TIMESTAMP WITH TIME ZONE': 'TIMESTAMP WITH TIME ZONE',
        'TIMESTAMP WITH LOCAL TIME ZONE': 'TIMESTAMP',
        'INTERVAL YEAR TO MONTH': 'INTERVAL',
        'INTERVAL DAY TO SECOND': 'INTERVAL',
        'CLOB': 'TEXT',
        'NCLOB': 'TEXT',
        'BLOB': 'BYTEA',
        'RAW': 'BYTEA',
        'LONG': 'TEXT',
        'LONG RAW': 'BYTEA',
        'ROWID': 'TEXT',
        'UROWID': 'TEXT',
    }
    
    @staticmethod
    def map_type(oracle_type: str, data_length: int = None, 
                 data_precision: int = None, data_scale: int = None) -> str:
        """
        Map Oracle data type to PostgreSQL equivalent.
        
        Args:
            oracle_type: Oracle data type name
            data_length: Maximum length for character types
            data_precision: Precision for numeric types
            data_scale: Scale for numeric types
            
        Returns:
            PostgreSQL data type string
        """
        oracle_type_upper = oracle_type.upper()
        
        # Handle special cases
        if oracle_type_upper == 'NUMBER':
            if data_precision is None:
                return 'NUMERIC'
            elif data_scale is None or data_scale == 0:
                if data_precision <= 4:
                    return 'SMALLINT'
                elif data_precision <= 9:
                    return 'INTEGER'
                elif data_precision <= 18:
                    return 'BIGINT'
                else:
                    return f'NUMERIC({data_precision})'
            else:
                return f'NUMERIC({data_precision},{data_scale})'
        
        elif oracle_type_upper in ('VARCHAR2', 'NVARCHAR2', 'VARCHAR'):
            if data_length:
                # PostgreSQL VARCHAR max is 10485760, but we'll cap at reasonable size
                max_length = min(data_length, 10485760)
                return f'VARCHAR({max_length})'
            else:
                return 'VARCHAR'
        
        elif oracle_type_upper in ('CHAR', 'NCHAR'):
            if data_length:
                return f'CHAR({data_length})'
            else:
                return 'CHAR(1)'
        
        elif oracle_type_upper == 'DATE':
            return 'TIMESTAMP'
        
        elif oracle_type_upper == 'TIMESTAMP':
            if data_scale:
                return f'TIMESTAMP({data_scale})'
            else:
                return 'TIMESTAMP'
        
        elif oracle_type_upper in ('CLOB', 'NCLOB', 'LONG'):
            return 'TEXT'
        
        elif oracle_type_upper in ('BLOB', 'RAW', 'LONG RAW'):
            return 'BYTEA'
        
        # Default mapping
        if oracle_type_upper in TypeMapper.TYPE_MAPPING:
            mapped = TypeMapper.TYPE_MAPPING[oracle_type_upper]
            return mapped
        
        # Unknown type - log warning and use TEXT as fallback
        logger.warning(f"Unknown Oracle type: {oracle_type}, mapping to TEXT")
        return 'TEXT'
    
    @staticmethod
    def convert_default_value(default_value: str, oracle_type: str) -> str:
        """
        Convert Oracle default value to PostgreSQL compatible format.
        
        Args:
            default_value: Oracle default value string
            oracle_type: Oracle data type
            
        Returns:
            PostgreSQL compatible default value
        """
        if not default_value:
            return None
        
        default_value = default_value.strip()
        oracle_type_upper = oracle_type.upper()
        
        # Remove Oracle-specific functions and convert
        if default_value.upper().startswith('SYSDATE'):
            return 'CURRENT_TIMESTAMP'
        elif default_value.upper().startswith('SYSTIMESTAMP'):
            return 'CURRENT_TIMESTAMP'
        elif default_value.upper().startswith('USER'):
            return 'CURRENT_USER'
        elif default_value.upper().startswith('SYS_GUID()'):
            return 'gen_random_uuid()'
        
        # Handle sequence.nextval
        if '.NEXTVAL' in default_value.upper():
            # This would need custom handling based on your sequences
            logger.warning(f"Sequence default value found: {default_value}, may need manual conversion")
            return None
        
        # For string defaults, remove quotes if they exist and re-add properly
        if oracle_type_upper in ('VARCHAR2', 'NVARCHAR2', 'CHAR', 'NCHAR', 'CLOB', 'NCLOB'):
            if default_value.startswith("'") and default_value.endswith("'"):
                return default_value  # Already quoted
            elif not default_value.startswith("'"):
                return f"'{default_value}'"
        
        return default_value

