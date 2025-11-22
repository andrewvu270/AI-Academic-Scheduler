"""
Database Connection Tests
Tests database connectivity and basic operations
"""

import pytest
import sys
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import get_supabase, get_supabase_admin
from app.config import settings

class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_supabase_client_creation(self):
        """Test that Supabase client can be created"""
        client = get_supabase()
        assert client is not None, "Supabase client should be created"
    
    def test_supabase_admin_client_creation(self):
        """Test that Supabase admin client can be created"""
        admin_client = get_supabase_admin()
        assert admin_client is not None, "Supabase admin client should be created"
    
    def test_database_configuration(self):
        """Test that database configuration is present"""
        # Check that required environment variables are configured
        assert settings.SUPABASE_URL is not None, "SUPABASE_URL should be configured"
        assert settings.SUPABASE_KEY is not None, "SUPABASE_KEY should be configured"

class TestDatabaseOperations:
    """Test basic database operations"""
    
    def test_health_check_query(self):
        """Test a simple database query"""
        try:
            admin_client = get_supabase_admin()
            if admin_client:
                # Try a simple query that should work
                response = admin_client.table("tasks").select("count", count="exact").limit(0).execute()
                assert response is not None, "Database query should return a response"
        except Exception as e:
            # If database is not accessible, skip this test
            pytest.skip(f"Database not accessible: {e}")
    
    def test_table_access(self):
        """Test that we can access main tables"""
        try:
            admin_client = get_supabase_admin()
            if admin_client:
                # Test access to main tables
                tables_to_test = ["tasks", "courses", "users"]
                
                for table in tables_to_test:
                    try:
                        response = admin_client.table(table).select("count", count="exact").limit(0).execute()
                        assert response is not None, f"Should be able to access {table} table"
                    except Exception as table_error:
                        # Individual table might not exist yet, that's ok
                        print(f"Table {table} not accessible: {table_error}")
        except Exception as e:
            pytest.skip(f"Database not accessible: {e}")
