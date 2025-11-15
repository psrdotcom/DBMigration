#!/usr/bin/env python3
"""
Basic tests for the DBMigration tool.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from agents.agent_router import AgentRouter
        print("  ✓ AgentRouter imported")
    except Exception as e:
        print(f"  ✗ AgentRouter import failed: {e}")
        return False
    
    try:
        from agents.base_agent import BaseAgent, LLMProvider
        print("  ✓ BaseAgent imported")
    except Exception as e:
        print(f"  ✗ BaseAgent import failed: {e}")
        return False
    
    try:
        from agents.schema_agent import SchemaAgent
        print("  ✓ SchemaAgent imported")
    except Exception as e:
        print(f"  ✗ SchemaAgent import failed: {e}")
        return False
    
    try:
        from agents.data_agent import DataAgent
        print("  ✓ DataAgent imported")
    except Exception as e:
        print(f"  ✗ DataAgent import failed: {e}")
        return False
    
    try:
        from agents.validation_agent import ValidationAgent
        print("  ✓ ValidationAgent imported")
    except Exception as e:
        print(f"  ✗ ValidationAgent import failed: {e}")
        return False
    
    try:
        from agents.query_agent import QueryAgent
        print("  ✓ QueryAgent imported")
    except Exception as e:
        print(f"  ✗ QueryAgent import failed: {e}")
        return False
    
    try:
        from src.utils.config_loader import load_config, get_db_connections
        print("  ✓ Config loader imported")
    except Exception as e:
        print(f"  ✗ Config loader import failed: {e}")
        return False
    
    try:
        from src.migration.type_mapper import TypeMapper
        print("  ✓ TypeMapper imported")
    except Exception as e:
        print(f"  ✗ TypeMapper import failed: {e}")
        return False
    
    return True


def test_agent_router():
    """Test AgentRouter initialization and basic functionality."""
    print("\nTesting AgentRouter...")
    
    try:
        from agents.agent_router import AgentRouter
        
        router = AgentRouter()
        print("  ✓ AgentRouter initialized")
        
        agents = router.list_agents()
        print(f"  ✓ Found {len(agents)} agents: {', '.join(agents)}")
        
        capabilities = router.get_agent_capabilities()
        print(f"  ✓ Retrieved capabilities for {len(capabilities)} agents")
        
        return True
    except Exception as e:
        print(f"  ✗ AgentRouter test failed: {e}")
        return False


def test_agent_initialization():
    """Test individual agent initialization."""
    print("\nTesting agent initialization...")
    
    try:
        from agents.schema_agent import SchemaAgent
        from agents.data_agent import DataAgent
        from agents.validation_agent import ValidationAgent
        from agents.query_agent import QueryAgent
        
        schema_agent = SchemaAgent()
        print("  ✓ SchemaAgent initialized")
        assert schema_agent.name == "SchemaAgent"
        
        data_agent = DataAgent()
        print("  ✓ DataAgent initialized")
        assert data_agent.name == "DataAgent"
        
        validation_agent = ValidationAgent()
        print("  ✓ ValidationAgent initialized")
        assert validation_agent.name == "ValidationAgent"
        
        query_agent = QueryAgent()
        print("  ✓ QueryAgent initialized")
        assert query_agent.name == "QueryAgent"
        
        return True
    except Exception as e:
        print(f"  ✗ Agent initialization test failed: {e}")
        return False


def test_agent_capabilities():
    """Test agent capability detection."""
    print("\nTesting agent capabilities...")
    
    try:
        from agents.agent_router import AgentRouter
        
        router = AgentRouter()
        
        # Test schema task routing
        schema_task = {'type': 'schema_migration'}
        agent = router.route_task(schema_task)
        assert agent is not None, "Should route schema task to an agent"
        print(f"  ✓ Schema task routed to: {agent.name}")
        
        # Test data task routing
        data_task = {'type': 'data_migration'}
        agent = router.route_task(data_task)
        assert agent is not None, "Should route data task to an agent"
        print(f"  ✓ Data task routed to: {agent.name}")
        
        # Test validation task routing
        validation_task = {'type': 'validate'}
        agent = router.route_task(validation_task)
        assert agent is not None, "Should route validation task to an agent"
        print(f"  ✓ Validation task routed to: {agent.name}")
        
        # Test query task routing
        query_task = {'type': 'convert_query', 'query': 'SELECT * FROM users'}
        agent = router.route_task(query_task)
        assert agent is not None, "Should route query task to an agent"
        print(f"  ✓ Query task routed to: {agent.name}")
        
        return True
    except Exception as e:
        print(f"  ✗ Agent capability test failed: {e}")
        return False


def test_type_mapper():
    """Test TypeMapper functionality."""
    print("\nTesting TypeMapper...")
    
    try:
        from src.migration.type_mapper import TypeMapper
        
        mapper = TypeMapper()
        
        # Test basic type mappings
        assert mapper.map_type('VARCHAR2', 100) == 'VARCHAR(100)'
        print("  ✓ VARCHAR2 mapping correct")
        
        assert mapper.map_type('NUMBER', 10, 2) == 'NUMERIC(10,2)'
        print("  ✓ NUMBER mapping correct")
        
        assert mapper.map_type('DATE') == 'TIMESTAMP'
        print("  ✓ DATE mapping correct")
        
        assert mapper.map_type('CLOB') == 'TEXT'
        print("  ✓ CLOB mapping correct")
        
        return True
    except Exception as e:
        print(f"  ✗ TypeMapper test failed: {e}")
        return False


def test_config_loader():
    """Test configuration loading."""
    print("\nTesting config loader...")
    
    try:
        from src.utils.config_loader import load_config
        from pathlib import Path
        
        config_path = Path(__file__).parent.parent / 'config' / 'config.yaml.example'
        
        if config_path.exists():
            config = load_config(str(config_path))
            print("  ✓ Config file loaded")
            
            # Check required sections
            assert 'oracle' in config or 'postgresql' in config, "Config should have database sections"
            print("  ✓ Config structure valid")
        else:
            print("  ⚠ Config example file not found (skipping)")
        
        return True
    except Exception as e:
        print(f"  ✗ Config loader test failed: {e}")
        return False


def test_query_agent_validation():
    """Test QueryAgent input validation."""
    print("\nTesting QueryAgent validation...")
    
    try:
        from agents.query_agent import QueryAgent
        
        agent = QueryAgent()
        
        # Test empty query
        result = agent.execute({'type': 'convert_query', 'query': ''})
        assert result['status'] == 'error', "Should reject empty query"
        print("  ✓ Empty query rejected")
        
        # Test missing query
        result = agent.execute({'type': 'convert_query'})
        assert result['status'] == 'error', "Should reject missing query"
        print("  ✓ Missing query rejected")
        
        # Test invalid query type
        result = agent.execute({'type': 'convert_query', 'query': 123})
        assert result['status'] == 'error', "Should reject non-string query"
        print("  ✓ Non-string query rejected")
        
        return True
    except Exception as e:
        print(f"  ✗ QueryAgent validation test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("DBMigration Tool - Basic Tests")
    print("=" * 60)
    
    tests = [
        ("Imports", test_imports),
        ("Agent Router", test_agent_router),
        ("Agent Initialization", test_agent_initialization),
        ("Agent Capabilities", test_agent_capabilities),
        ("Type Mapper", test_type_mapper),
        ("Config Loader", test_config_loader),
        ("Query Agent Validation", test_query_agent_validation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n  ✗ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())

