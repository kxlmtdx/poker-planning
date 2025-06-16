import pyodbc, uuid
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
    def create_session(self, group_id: int, group_name: str, created_by: int) -> str:
        self.cursor.execute(
            "IF NOT EXISTS (SELECT 1 FROM Groups WHERE GroupId = ?) "
            "INSERT INTO Groups (GroupId, GroupName, CreatedBy, IsActive) "
            "VALUES (?, ?, ?, 1)",
            (group_id, group_id, group_name, created_by)
        )

        self.cursor.execute(
            "SELECT SessionId FROM Sessions WHERE GroupId = ? AND Status = 'Closed'",
            (group_id,)
        )
        existing_session = self.cursor.fetchone()

        if existing_session:
            session_id = existing_session[0]
            self.cursor.execute(
                "UPDATE Sessions SET Status = 'Active', StartDate = GETDATE(), EndDate = NULL "
                "WHERE SessionId = ?",
                (session_id,)
            )
        else:
            session_id = str(uuid.uuid4())
            self.cursor.execute(
                "INSERT INTO Sessions (SessionId, GroupId, CreatedBy, StartDate, Status) "
                "VALUES (?, ?, ?, GETDATE(), 'Active')",
                (session_id, group_id, created_by)
            )

        self.cursor.execute(
            "UPDATE Groups SET GroupName = ?, IsActive = 1 WHERE GroupId = ?",
            (group_name, group_id)
        )

        self.cursor.execute(
            "IF NOT EXISTS (SELECT 1 FROM GroupMembers WHERE GroupId = ? AND UserId = ?) "
            "INSERT INTO GroupMembers (GroupId, UserId, JoinDate) VALUES (?, ?, GETDATE())",
            (group_id, created_by, group_id, created_by)
        )

        self.conn.commit()
        return session_id
    
    def close_session(self, session_id: uuid.UUID) -> bool:
        self.cursor.execute(
            "UPDATE Sessions SET Status = 'Closed', EndDate = GETDATE() "
            "WHERE SessionId = ?",
            (session_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount > 0


# Issue op
    def create_issue(self, session_id: str, title: str, description: str, created_by: int) -> str:
        issue_id = str(uuid.uuid4())
        self.cursor.execute(
            "INSERT INTO Issues (IssueId, SessionId, Title, Description, "
            "CreatedBy, CreationDate, Status) "
            "VALUES (?, ?, ?, ?, ?, GETDATE(), 'Voting')",
            (issue_id, session_id, title, description, created_by)
        )
        self.conn.commit()
        return issue_id
    
    def finalize_issue(self, issue_id: str, final_estimate: float) -> bool:
        self.cursor.execute(
            "UPDATE Issues SET Status = 'Completed', FinalEstimate = ?, FinalizedDate = GETDATE() "
            "WHERE IssueId = ?",
            (final_estimate, issue_id)
        )

        self.cursor.execute(
            "DELETE FROM VotingMessages WHERE IssueId = ?",
            (issue_id,)
        )
        
        self.conn.commit()
        return self.cursor.rowcount > 0




# Vote op





# Group op





# Utils