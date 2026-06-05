import datetime
import os
from pymongo import MongoClient

class MongoDBLogger:
    def __init__(self):
        # Membaca URI MongoDB dari internal Docker Network
        mongo_uri = os.environ.get("MONGO_URI", "mongodb://admin:mongo_pass@mongodb:27017/")
        self.client = MongoClient(mongo_uri)
        # Membuat atau menggunakan database bernama 'simple_lms_logs'
        self.db = self.client["simple_lms_logs"]
        
    def log_activity(self, user_id: int, username: str, activity_type: str, details: dict):
        """
        DELIVERABLE: Menyimpan log jejak aktivitas user (Activity Log Collection)
        """
        collection = self.db["activity_logs"]
        log_document = {
            "user_id": user_id,
            "username": username,
            "activity_type": activity_type,  # Contoh: 'VIEW_COURSE', 'ENROLL_COURSE'
            "details": details,
            "timestamp": datetime.datetime.utcnow()
        }
        return collection.insert_one(log_document)

    def log_analytics(self, course_id: int, student_count: int, completion_rate: float):
        """
        DELIVERABLE: Menyimpan data analitik pembelajaran (Learning Analytics Collection)
        """
        collection = self.db["learning_analytics"]
        analytics_document = {
            "course_id": course_id,
            "total_students": student_count,
            "completion_rate": completion_rate,
            "updated_at": datetime.datetime.utcnow()
        }
        return collection.replace_one({"course_id": course_id}, analytics_document, upsert=True)

# Inisialisasi object secara global agar bisa di-import langsung di api.py
mongo_logger = MongoDBLogger()