#!/usr/bin/env python3
"""
MentorAI - Sistema de Actualizaciones Automáticas
Verifica y descarga actualizaciones de forma segura
"""

import json
import os
import hashlib
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError


class UpdateManager:
    """Gestor de actualizaciones automáticas"""
    
    def __init__(self, app_version="1.0.0", update_url="https://updates.mentorai.com"):
        self.app_version = app_version
        self.update_url = update_url
        self.app_dir = Path(__file__).parent.parent
        self.update_log_path = Path.home() / ".mentorai" / "updates.log"
        self.update_log_path.parent.mkdir(exist_ok=True)
    
    def get_latest_version(self):
        """Obtener versión más reciente disponible"""
        try:
            # En producción, esto consultaría un servidor
            # Por ahora, retornamos versión local
            return {
                "version": self.app_version,
                "release_date": datetime.now().isoformat(),
                "changelog": "Versión inicial",
                "download_url": None,
                "checksum": None
            }
        except Exception as e:
            self.log_update(f"Error al obtener versión: {e}")
            return None
    
    def check_for_updates(self):
        """Verificar si hay actualizaciones disponibles"""
        try:
            latest = self.get_latest_version()
            
            if not latest:
                return False
            
            # Comparar versiones
            if self.compare_versions(latest["version"], self.app_version) > 0:
                self.log_update(f"Actualización disponible: {latest['version']}")
                return True
            
            return False
        
        except Exception as e:
            self.log_update(f"Error al verificar actualizaciones: {e}")
            return False
    
    def compare_versions(self, v1, v2):
        """Comparar dos versiones (v1 > v2 retorna 1, v1 < v2 retorna -1, igual retorna 0)"""
        def normalize(v):
            return [int(x) for x in v.split(".")]
        
        try:
            v1_parts = normalize(v1)
            v2_parts = normalize(v2)
            
            # Rellenar con ceros si es necesario
            max_len = max(len(v1_parts), len(v2_parts))
            v1_parts += [0] * (max_len - len(v1_parts))
            v2_parts += [0] * (max_len - len(v2_parts))
            
            if v1_parts > v2_parts:
                return 1
            elif v1_parts < v2_parts:
                return -1
            else:
                return 0
        except:
            return 0
    
    def download_update(self, download_url, checksum=None):
        """Fail closed until a signed, authenticated updater is implemented.

        A prior placeholder returned a path to a non-existent archive and
        incorrectly reported download success. No files are downloaded.
        """
        self.log_update(
            "Actualización automática no disponible: descarga autenticada y "
            "validación criptográfica pendientes. Utiliza el instalador oficial."
        )
        return False

    def calculate_checksum(self, file_path):
        """Calcular checksum SHA256 de un archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def install_update(self, update_file):
        """Never report an installation that was not actually performed.

        Installation requires package signature verification and a controlled,
        recoverable updater outside the running application's directory.
        """
        self.log_update(
            "Instalación automática bloqueada: la función de instalación "
            "segura no está implementada."
        )
        return False

    def rollback_update(self):
        """Do not destroy an installation from an unverified backup.

        The automatic installer is intentionally disabled until signed,
        authenticated updates and an atomic rollback mechanism are available.
        The previous implementation removed the running application directory
        before checking integrity or being able to restore it safely.
        """
        self.log_update(
            "Rollback automático bloqueado: aún no existe un mecanismo "
            "atómico y firmado de recuperación. La instalación no se modificó."
        )
        return False

    def log_update(self, message):
        """Registrar evento de actualización"""
        timestamp = datetime.now().isoformat()
        log_message = f"[{timestamp}] {message}\n"
        
        with open(self.update_log_path, 'a') as f:
            f.write(log_message)
    
    def get_update_history(self):
        """Obtener historial de actualizaciones"""
        if not self.update_log_path.exists():
            return []
        
        with open(self.update_log_path, 'r') as f:
            return f.readlines()
    
    def enable_auto_updates(self):
        """Refuse to advertise an updater that cannot authenticate packages.

        The downloader, installer and rollback deliberately fail closed. Do not
        persist auto_updates=True until all three operations are implemented
        and verified; preserve existing user configuration untouched.
        """
        self.log_update(
            "Actualizaciones automáticas no disponibles: se requiere descarga "
            "autenticada, firma verificada y recuperación atómica."
        )
        return False
    
    def disable_auto_updates(self):
        """Deshabilitar actualizaciones automáticas"""
        config_path = Path.home() / ".mentorai" / "config.json"
        
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        config['auto_updates'] = False
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_update("Actualizaciones automáticas deshabilitadas")


class AutoUpdateService:
    """Servicio de actualización automática (ejecutable en background)"""
    
    def __init__(self, app_version="1.0.0"):
        self.updater = UpdateManager(app_version)
        self.running = False
    
    def start(self):
        """Iniciar servicio de actualización"""
        self.running = True
        self.updater.log_update("Servicio de actualización iniciado")
    
    def stop(self):
        """Detener servicio de actualización"""
        self.running = False
        self.updater.log_update("Servicio de actualización detenido")
    
    def check_and_update(self):
        """Verificar e instalar actualizaciones"""
        if not self.running:
            return False
        
        if self.updater.check_for_updates():
            latest = self.updater.get_latest_version()
            
            if latest and latest.get('download_url'):
                update_file = self.updater.download_update(
                    latest['download_url'],
                    latest.get('checksum')
                )
                
                if update_file:
                    return self.updater.install_update(update_file)
        
        return False


if __name__ == "__main__":
    # Prueba del updater
    updater = UpdateManager()
    
    print("=== SISTEMA DE ACTUALIZACIONES MENTORAI ===\n")
    print(f"Versión actual: {updater.app_version}")
    print(f"Verificando actualizaciones...")
    
    if updater.check_for_updates():
        print("✅ Actualizaciones disponibles")
    else:
        print("✅ Ya tienes la versión más reciente")
    
    print("\n=== HISTORIAL DE ACTUALIZACIONES ===")
    history = updater.get_update_history()
    for entry in history[-5:]:  # Últimas 5 entradas
        print(entry.strip())
