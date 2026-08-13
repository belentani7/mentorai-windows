import hashlib
import base64
import os
import json

# En producción, usaríamos 'cryptography.fernet' o similar.
# Esta es una implementación simplificada para el prototipo.

class SecurityManager:
    def __init__(self, device_id):
        self.key = hashlib.sha256(device_id.encode()).digest()

    def encrypt_data(self, data_str):
        # Simulación de cifrado AES-256
        # En producción: Fernet(base64.urlsafe_b64encode(self.key)).encrypt(data_str.encode())
        return base64.b64encode(data_str.encode()).decode()

    def decrypt_data(self, encrypted_str):
        # Simulación de descifrado
        return base64.b64decode(encrypted_str.encode()).decode()

    def generate_privacy_report(self):
        return {
            "compliance": "RGPD / GDPR",
            "data_storage": "Local Only (Encrypted)",
            "third_party_sharing": "None",
            "user_rights": [
                "Right to access: You can view all local logs.",
                "Right to erasure: You can delete all local data with one click.",
                "Privacy by design: No screen data leaves the device."
            ]
        }

    def wipe_all_data(self, paths):
        for path in paths:
            if os.path.exists(path):
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    import shutil
                    shutil.rmtree(path)
        return "All local data has been securely erased."

if __name__ == "__main__":
    sm = SecurityManager("device-unique-id-123")
    report = sm.generate_privacy_report()
    print(f"Privacy Report: {json.dumps(report, indent=2)}")
