import pyodbc
from typing import Dict, Any, List, Optional


class Database:
    def __init__(self, config: Dict[str, Any]):
        if not all(key in config for key in ['server', 'database', 'username', 'password']):
            raise ValueError("Invalid database configuration")
            
        self.conn = pyodbc.connect(
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={config['server']};"
            f"DATABASE={config['database']};"
            f"UID={config['username']};"
            f"PWD={config['password']};"
        )
        self.cursor = self.conn.cursor()


# User op





# Session op





# Issue op





# Vote op





# Group op





# Utils