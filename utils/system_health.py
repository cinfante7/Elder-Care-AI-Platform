"""
Elder Assistant System Health Monitor
Provides testing utilities and system validation for comprehensive testing phase
"""

import os
import json
import time
import datetime
import sqlite3
from pathlib import Path
import streamlit as st

class SystemHealthMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / "data"
        self.db_path = self.project_root / "db" / "elder_assistant.db"
        
    def check_system_health(self):
        """Comprehensive system health check"""
        health_report = {
            "timestamp": datetime.datetime.now().isoformat(),
            "overall_status": "HEALTHY",
            "critical_issues": [],
            "warnings": [],
            "components": {}
        }
        
        # Check file system components
        health_report["components"]["filesystem"] = self._check_filesystem()
        
        # Check database connectivity
        health_report["components"]["database"] = self._check_database()
        
        # Check admin credentials
        health_report["components"]["admin_auth"] = self._check_admin_auth()
        
        # Check voice model
        health_report["components"]["voice_model"] = self._check_voice_model()
        
        # Determine overall status
        if any(comp["status"] == "ERROR" for comp in health_report["components"].values()):
            health_report["overall_status"] = "CRITICAL"
        elif any(comp["status"] == "WARNING" for comp in health_report["components"].values()):
            health_report["overall_status"] = "WARNING"
            
        return health_report
    
    def _check_filesystem(self):
        """Check critical files and directories"""
        result = {"status": "HEALTHY", "details": {}}
        
        critical_files = [
            "main.py",
            "auth.py",
            "data/admin_credentials.json",
            "data/config.json",
            "db/elder_assistant.db"
        ]
        
        for file_path in critical_files:
            full_path = self.project_root / file_path
            exists = full_path.exists()
            result["details"][file_path] = {
                "exists": exists,
                "size": full_path.stat().st_size if exists else 0
            }
            if not exists and file_path in ["main.py", "auth.py"]:
                result["status"] = "ERROR"
            elif not exists:
                result["status"] = "WARNING"
                
        return result
    
    def _check_database(self):
        """Check database connectivity and tables"""
        result = {"status": "HEALTHY", "details": {}}
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Check if main tables exist
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            
            result["details"]["tables"] = tables
            result["details"]["connection"] = "SUCCESS"
            
            # Check some basic functionality
            cursor.execute("SELECT COUNT(*) FROM conversations;")
            conversation_count = cursor.fetchone()[0]
            result["details"]["conversation_count"] = conversation_count
            
            conn.close()
            
        except Exception as e:
            result["status"] = "ERROR"
            result["details"]["error"] = str(e)
            
        return result
    
    def _check_admin_auth(self):
        """Check admin authentication system"""
        result = {"status": "HEALTHY", "details": {}}
        
        try:
            with open(self.data_dir / "admin_credentials.json", "r") as f:
                admin_creds = json.load(f)
                
            result["details"]["admin_count"] = len(admin_creds)
            result["details"]["admin_users"] = list(admin_creds.keys())
            
            # Validate structure
            for user_id, user_data in admin_creds.items():
                required_fields = ["username", "password", "role", "name"]
                missing_fields = [field for field in required_fields if field not in user_data]
                if missing_fields:
                    result["status"] = "WARNING"
                    result["details"]["missing_fields"] = missing_fields
                    
        except Exception as e:
            result["status"] = "ERROR"
            result["details"]["error"] = str(e)
            
        return result
    
    def _check_voice_model(self):
        """Check voice recognition model"""
        result = {"status": "HEALTHY", "details": {}}
        
        model_path = self.project_root / "models" / "vosk-model-small-en-us-0.15"
        
        if model_path.exists():
            result["details"]["model_exists"] = True
            result["details"]["model_size"] = sum(f.stat().st_size for f in model_path.rglob('*') if f.is_file())
        else:
            result["status"] = "ERROR"
            result["details"]["model_exists"] = False
            
        return result

def run_performance_test():
    """Run basic performance tests"""
    results = {
        "timestamp": datetime.datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Database query performance
    start_time = time.time()
    try:
        from db.database import get_last_n_conversations
        conversations = get_last_n_conversations(10)
        end_time = time.time()
        results["tests"]["database_query"] = {
            "status": "PASS",
            "duration": end_time - start_time,
            "records_retrieved": len(conversations)
        }
    except Exception as e:
        results["tests"]["database_query"] = {
            "status": "FAIL",
            "error": str(e)
        }
    
    # Test 2: Configuration loading
    start_time = time.time()
    try:
        from core.config_manager import load_user_config
        config = load_user_config()
        end_time = time.time()
        results["tests"]["config_loading"] = {
            "status": "PASS",
            "duration": end_time - start_time,
            "config_keys": list(config.keys())
        }
    except Exception as e:
        results["tests"]["config_loading"] = {
            "status": "FAIL",
            "error": str(e)
        }
    
    return results

def generate_test_report():
    """Generate comprehensive test report"""
    monitor = SystemHealthMonitor()
    
    report = {
        "system_health": monitor.check_system_health(),
        "performance_tests": run_performance_test(),
        "testing_checklist": {
            "functional_tests": {
                "login_system": "PENDING",
                "voice_recording": "PENDING",
                "interface_separation": "PENDING",
                "admin_dashboard": "PENDING",
                "resident_interface": "PENDING"
            },
            "performance_tests": {
                "system_load": "PENDING",
                "response_times": "PENDING"
            },
            "edge_case_tests": {
                "error_handling": "PENDING",
                "boundary_testing": "PENDING"
            }
        },
        "stakeholder_feedback": {
            "professor_feedback": "PENDING",
            "simulated_users": "PENDING"
        }
    }
    
    return report

if __name__ == "__main__":
    report = generate_test_report()
    print(json.dumps(report, indent=2))