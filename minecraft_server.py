# ================================
# start.sh - Script de inicio rápido
# ================================
#!/bin/bash

clear
echo "🎮 Iniciando Servidor de Minecraft para Codespace..."
echo "=================================================="

# Verificar si Python está disponible
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 no está instalado"
    exit 1
fi

# Verificar si el script principal existe
if [ ! -f "minecraft_server.py" ]; then
    echo "❌ minecraft_server.py no encontrado"
    exit 1
fi

# Instalar dependencias si es necesario
if [ -f "requirements.txt" ]; then
    echo "📦 Instalando dependencias..."
    pip3 install -r requirements.txt > /dev/null 2>&1
fi

# Ejecutar el servidor
echo "🚀 Iniciando servidor..."
python3 minecraft_server.py

# ================================
# .gitignore
# ================================
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Minecraft Server
minecraft_server/
world/
world_nether/
world_the_end/
*.jar
eula.txt
server.properties
ops.json
whitelist.json
banned-players.json
banned-ips.json
usercache.json
usernamecache.json
logs/
crash-reports/
plugins/
mods/
config/
saves/

# ngrok
ngrok
ngrok.exe

# System
.DS_Store
Thumbs.db

# Temporary files
*.tmp
*.temp
*.log

# ================================
# LICENSE
# ================================
MIT License

Copyright (c) 2025 Minecraft Server Codespace

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

# ================================
# backup.sh - Script de respaldo
# ================================
#!/bin/bash

BACKUP_DIR="backups"
WORLD_DIR="minecraft_server/world"
DATE=$(date +%Y%m%d_%H%M%S)

echo "💾 Creando respaldo del mundo..."

# Crear directorio de respaldos si no existe
mkdir -p $BACKUP_DIR

# Verificar si existe el mundo
if [ ! -d "$WORLD_DIR" ]; then
    echo "❌ No se encontró el directorio del mundo"
    exit 1
fi

# Crear respaldo
BACKUP_FILE="$BACKUP_DIR/world_backup_$DATE.tar.gz"
tar -czf "$BACKUP_FILE" -C minecraft_server world

if [ $? -eq 0 ]; then
    echo "✅ Respaldo creado: $BACKUP_FILE"
    
    # Mostrar tamaño del respaldo
    SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
    echo "📦 Tamaño: $SIZE"
    
    # Limpiar respaldos antiguos (mantener solo los últimos 5)
    cd $BACKUP_DIR
    ls -t world_backup_*.tar.gz | tail -n +6 | xargs -r rm
    echo "🧹 Respaldos antiguos limpiados"
else
    echo "❌ Error creando el respaldo"
    exit 1
fi

# ================================
# monitor.py - Monitor del servidor
# ================================
#!/usr/bin/env python3
"""
Monitor simple para el servidor de Minecraft
Muestra estadísticas en tiempo real
"""

import psutil
import time
import sys
import subprocess
import json
import requests
from datetime import datetime

class ServerMonitor:
    def __init__(self):
        self.start_time = time.time()

    def clear_screen(self):
        subprocess.run('clear', shell=True)

    def get_system_stats(self):
        """Obtiene estadísticas del sistema"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu': cpu_percent,
            'memory_used': memory.used,
            'memory_total': memory.total,
            'memory_percent': memory.percent,
            'disk_used': disk.used,
            'disk_total': disk.total,
            'disk_percent': (disk.used / disk.total) * 100
        }

    def get_minecraft_process(self):
        """Busca el proceso de Minecraft"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if 'java' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'server.jar' in cmdline:
                        return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def get_ngrok_info(self):
        """Obtiene información de ngrok"""
        try:
            response = requests.get("http://localhost:4040/api/tunnels", timeout=2)
            tunnels = response.json()
            if tunnels["tunnels"]:
                return tunnels["tunnels"][0]["public_url"]
        except:
            pass
        return None

    def format_bytes(self, bytes_value):
        """Convierte bytes a formato legible"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"

    def run(self):
        """Ejecuta el monitor"""
        try:
            while True:
                self.clear_screen()
                
                print("🖥️  MONITOR DEL SERVIDOR DE MINECRAFT")
                print("=" * 50)
                print(f"⏰ Tiempo ejecutándose: {int(time.time() - self.start_time)} segundos")
                print(f"🕒 Hora actual: {datetime.now().strftime('%H:%M:%S')}")
                print()
                
                # Estadísticas del sistema
                stats = self.get_system_stats()
                print("📊 ESTADÍSTICAS DEL SISTEMA:")
                print(f"   CPU: {stats['cpu']:.1f}%")
                print(f"   RAM: {self.format_bytes(stats['memory_used'])} / {self.format_bytes(stats['memory_total'])} ({stats['memory_percent']:.1f}%)")
                print(f"   Disco: {stats['disk_percent']:.1f}% usado")
                print()
                
                # Proceso de Minecraft
                minecraft_proc = self.get_minecraft_process()
                if minecraft_proc:
                    try:
                        mc_cpu = minecraft_proc.cpu_percent()
                        mc_memory = minecraft_proc.memory_info()
                        
                        print("🎮 SERVIDOR DE MINECRAFT:")
                        print(f"   Estado: ✅ EJECUTÁNDOSE")
                        print(f"   PID: {minecraft_proc.pid}")
                        print(f"   CPU: {mc_cpu:.1f}%")
                        print(f"   RAM: {self.format_bytes(mc_memory.rss)}")
                    except:
                        print("🎮 SERVIDOR DE MINECRAFT: ❌ ERROR OBTENIENDO DATOS")
                else:
                    print("🎮 SERVIDOR DE MINECRAFT: ❌ NO EJECUTÁNDOSE")
                
                print()
                
                # Información de ngrok
                ngrok_url = self.get_ngrok_info()
                if ngrok_url:
                    print(f"🌐 NGROK: ✅ ACTIVO")
                    print(f"   URL: {ngrok_url}")
                else:
                    print("🌐 NGROK: ❌ INACTIVO")
                
                print()
                print("Presiona Ctrl+C para salir")
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n👋 Monitor detenido")
            sys.exit(0)

if __name__ == "__main__":
    monitor = ServerMonitor()
    monitor.run()

# ================================
# install.py - Instalador automático para sistemas sin bash
# ================================
#!/usr/bin/env python3
"""
Instalador automático para entornos que no soportan bash
"""

import os
import sys
import subprocess
import platform

def run_command(command):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def install_dependencies():
    """Instala las dependencias necesarias"""
    print("📦 Instalando dependencias...")
    
    # Instalar dependencias de Python
    success, output = run_command("pip3 install requests urllib3")
    if not success:
        print(f"❌ Error instalando dependencias de Python: {output}")
        return False
    
    # Verificar si apt está disponible (sistemas basados en Debian/Ubuntu)
    if platform.system() == "Linux":
        success, _ = run_command("which apt-get")
        if success:
            print("🔧 Actualizando sistema...")
            run_command("sudo apt-get update > /dev/null 2>&1")
            
            print("📥 Instalando herramientas básicas...")
            run_command("sudo apt-get install -y curl wget unzip > /dev/null 2>&1")
    
    print("✅ Dependencias instaladas correctamente")
    return True

def setup_directories():
    """Crea los directorios necesarios"""
    directories = [
        "minecraft_server",
        "backups",
        ".devcontainer"
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"📁 Directorio creado: {directory}")

def make_executable():
    """Hace los scripts ejecutables"""
    scripts = [
        "minecraft_server.py",
        "start.sh",
        "backup.sh",
        "monitor.py"
    ]
    
    for script in scripts:
        if os.path.exists(script):
            os.chmod(script, 0o755)
            print(f"🔧 Script ejecutable: {script}")

def main():
    """Función principal del instalador"""
    print("🚀 INSTALADOR DE SERVIDOR DE MINECRAFT")
    print("=====================================")
    
    # Verificar Python
    if sys.version_info < (3, 6):
        print("❌ Se requiere Python 3.6 o superior")
        sys.exit(1)
    
    print(f"✅ Python {sys.version} encontrado")
    
    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)
    
    # Configurar directorios
    setup_directories()
    
    # Hacer scripts ejecutables
    make_executable()
    
    print("\n✅ INSTALACIÓN COMPLETADA")
    print("Para iniciar el servidor, ejecuta:")
    print("   python3 minecraft_server.py")
    print("o")
    print("   ./start.sh")

if __name__ == "__main__":
    main()
