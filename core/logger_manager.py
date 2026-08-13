import os
import json
import datetime
import hashlib

class SecureLogger:
    def __init__(self, log_dir):
        self.log_dir = log_dir
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def _anonymize_user(self, user_id):
        return hashlib.sha256(user_id.encode()).hexdigest()[:12]

    def log_event(self, user_id, event_type, details):
        timestamp = datetime.datetime.now().isoformat()
        anon_id = self._anonymize_user(user_id)
        
        log_entry = {
            "timestamp": timestamp,
            "user_id": anon_id,
            "event": event_type,
            "details": details
        }
        
        log_file = os.path.join(self.log_dir, f"log_{datetime.date.today().isoformat()}.jsonl")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_all_logs(self):
        logs = []
        for filename in sorted(os.listdir(self.log_dir)):
            if filename.endswith(".jsonl"):
                with open(os.path.join(self.log_dir, filename), "r", encoding="utf-8") as f:
                    for line in f:
                        logs.append(json.loads(line))
        return logs

    def clear_logs(self):
        for filename in os.listdir(self.log_dir):
            os.remove(os.path.join(self.log_dir, filename))
        return "Todos los logs locales han sido eliminados."

if __name__ == "__main__":
    logger = SecureLogger("/home/ubuntu/asistente_educativo/logs")
    logger.log_event("user_123", "query", {"term": "cd", "status": "success"})
    print(f"Logs capturados: {len(logger.get_all_logs())}")
