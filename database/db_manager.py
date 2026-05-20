import sqlite3

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect("waste.db")
        self.cursor = self.conn.cursor()
        self.create_table()
    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_name TEXT,
            waste_category TEXT,
            risk_class TEXT,
            confidence REAL,
            detection_time TEXT
        )
        """)
        self.conn.commit()
        
    def insert_detection(
        self,
        object_name,
        waste_category,
        risk_class,
        confidence,
        detection_time
    ):
        self.cursor.execute("""
            INSERT INTO detections (
                object_name,
                waste_category,
                risk_class,
                confidence,
                detection_time
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            object_name,
            waste_category,
            risk_class,
            confidence,
            detection_time
        ))
        self.conn.commit()
    def close(self):
        self.conn.close()