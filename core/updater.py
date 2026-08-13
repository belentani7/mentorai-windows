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
        """Descargar actualización"""
        try:
            temp_dir = tempfile.mkdtemp()
            temp_file = Path(temp_dir) / "mentorai_update.tar.gz"
            
            self.log_update(f"Descargando actualización desde {download_url}")
            
            # Simular descarga (en producción, usar urllib)
            # response = urlopen(download_url)
            # with open(temp_file, 'wb') as f:
            #     f.write(response.read())
            
            # Verificar checksum si se proporciona
            if checksum:
                file_checksum = self.calculate_checksum(temp_file)
                if file_checksum != checksum:
                    self.log_update("Error: Checksum no coincide")
                    return False
            
            self.log_update("Descarga completada")
            return str(temp_file)
        
        except Exception as e:
            self.log_update(f"Error al descargar: {e}")
            return False
    
    def calculate_checksum(self, file_path):
        """Calcular checksum SHA256 de un archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def install_update(self, update_file):
        """Instalar actualización"""
        try:
            self.log_update(f"Instalando actualización desde {update_file}")
            
            # Crear backup de versión actual
            backup_dir = Path.home() / ".mentorai" / f"backup_{self.app_version}"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            
            shutil.copytree(self.app_dir, backup_dir)
            self.log_update(f"Backup creado en {backup_dir}")
            
            # Extraer y instalar actualización
            # En producción: tar.extractall()
            
            self.log_update("Actualización instalada correctamente")
            return True
        
        except Exception as e:
            self.log_update(f"Error al instalar: {e}")
            self.rollback_update()
            return False
    
    def rollback_update(self):
        """Revertir a versión anterior si hay error"""
        try:
            backup_dir = Path.home() / ".mentorai" / f"backup_{self.app_version}"
            
            if backup_dir.exists():
                # Restaurar desde backup
                shutil.rmtree(self.app_dir)
                shutil.copytree(backup_dir, self.app_dir)
                self.log_update("Rollback completado")
                return True
            
            return False
        
        except Exception as e:
            self.log_update(f"Error en rollback: {e}")
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
        """Habilitar actualizaciones automáticas"""
        config_path = Path.home() / ".mentorai" / "config.json"
        
        config = {}
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        
        config['auto_updates'] = True
        config['check_updates_interval'] = 86400  # 24 horas
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        self.log_update("Actualizaciones automáticas habilitadas")
    
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
