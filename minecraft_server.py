#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de Minecraft para GitHub Codespaces
Versión mejorada con soporte completo para ngrok y múltiples tipos de servidor
"""

import requests
import os
import base64
import glob
import time
import json
import subprocess
import zipfile
import shutil
import threading
from urllib.parse import urlparse

# Colores para la terminal
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_colored(text, color):
    print(f"{color}{text}{Colors.END}")

def print_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🎮 SERVIDOR DE MINECRAFT PARA GITHUB CODESPACES 🎮    ║
║                                                              ║
║              Creado con ❤️ para la comunidad                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """
    print_colored(banner, Colors.CYAN)

# Configuración de .gitignore
def setup_gitignore():
    if not os.path.exists("./.gitignore"):
        big = "L1B5dGhvbioNCi93b3JrX2FyZWEqDQovc2Vydmlkb3JfbWluZWNyYWZ0DQovbWluZWNyYWZ0X3NlcnZlcg0KL3NlcnZpZG9yX21pbmVjcmFmdF9vbGQNCi90YWlsc2NhbGUtY3MNCi90aGFub3MNCi9zZXJ2ZXJzDQovYmtkaXINCi92ZW5kb3INCmNvbXBvc2VyLioNCmNvbmZpZ3VyYXRpb24uanNvbg0KY29uZmlndXJhY2lvbi5qc29uDQoqLnR4dA0KKi5weWMNCioubXNwDQoqLm91dHB1dA=="
        dec = base64.standard_b64decode(big).decode()
        with open(".gitignore", 'w') as giti:
            giti.write(dec)

# URLs de descarga para diferentes versiones
MINECRAFT_VERSIONS = {
    "1.21.4": {
        "vanilla": "https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar",
        "paper": "https://api.papermc.io/v2/projects/paper/versions/1.21.4/builds/33/downloads/paper-1.21.4-33.jar",
        "fabric": "https://meta.fabricmc.net/v2/versions/loader/1.21.4/0.16.9/1.0.1/server/jar",
        "forge": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.21.4-52.0.1/forge-1.21.4-52.0.1-installer.jar"
    },
    "1.21.3": {
        "vanilla": "https://piston-data.mojang.com/v1/objects/45810d238246d90e811d896f87b14695b7fb6839/server.jar",
        "paper": "https://api.papermc.io/v2/projects/paper/versions/1.21.3/builds/109/downloads/paper-1.21.3-109.jar",
        "fabric": "https://meta.fabricmc.net/v2/versions/loader/1.21.3/0.16.9/1.0.1/server/jar",
        "forge": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.21.3-51.0.33/forge-1.21.3-51.0.33-installer.jar"
    },
    "1.20.1": {
        "vanilla": "https://piston-data.mojang.com/v1/objects/84194a2f286ef7c14ed7ce0090dba59902951553/server.jar",
        "paper": "https://api.papermc.io/v2/projects/paper/versions/1.20.1/builds/196/downloads/paper-1.20.1-196.jar",
        "fabric": "https://meta.fabricmc.net/v2/versions/loader/1.20.1/0.16.9/1.0.1/server/jar",
        "forge": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.20.1-47.3.0/forge-1.20.1-47.3.0-installer.jar"
    },
    "1.19.4": {
        "vanilla": "https://piston-data.mojang.com/v1/objects/8f3112a1049751cc472ec13e397eade5336ca7ae/server.jar",
        "paper": "https://api.papermc.io/v2/projects/paper/versions/1.19.4/builds/550/downloads/paper-1.19.4-550.jar",
        "fabric": "https://meta.fabricmc.net/v2/versions/loader/1.19.4/0.16.9/1.0.1/server/jar",
        "forge": "https://maven.minecraftforge.net/net/minecraftforge/forge/1.19.4-45.3.0/forge-1.19.4-45.3.0-installer.jar"
    }
}

NGROK_REGIONS = {
    "ap": "Asia / Pacífico (Singapore)",
    "au": "Australia (Sydney)",
    "eu": "Europa (Frankfurt)",
    "in": "India (Mumbai)",
    "jp": "Japón (Tokyo)",
    "sa": "Sudamérica (São Paulo)",
    "us": "Estados Unidos (Ohio)",
    "us-cal-1": "Estados Unidos (California)"
}

def install_dependencies():
    """Instala las dependencias necesarias"""
    print_colored("📦 Instalando dependencias...", Colors.YELLOW)
    
    # Instalar Java si no existe
    java_check = subprocess.run(["java", "-version"], capture_output=True, text=True)
    if java_check.returncode != 0:
        print_colored("☕ Instalando Java...", Colors.BLUE)
        os.system("sudo apt update && sudo apt install -y openjdk-21-jdk")
    
    # Instalar ngrok si no existe
    if not os.path.exists("/usr/local/bin/ngrok"):
        print_colored("🌐 Instalando ngrok...", Colors.BLUE)
        os.system("curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null")
        os.system("echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list")
        os.system("sudo apt update && sudo apt install ngrok")

def setup_ngrok_token():
    """Configura el token de ngrok"""
    print_colored("\n🔑 Configuración de ngrok", Colors.CYAN)
    
    # Verificar si ya hay un token configurado
    ngrok_config_path = os.path.expanduser("~/.config/ngrok/ngrok.yml")
    if os.path.exists(ngrok_config_path):
        print_colored("✅ Token de ngrok ya configurado", Colors.GREEN)
        return True
    
    token = input("Ingresa tu token de ngrok (puedes obtenerlo gratis en https://ngrok.com/): ").strip()
    
    if not token:
        print_colored("❌ Token requerido para continuar", Colors.RED)
        return False
    
    # Configurar ngrok
    result = os.system(f"ngrok config add-authtoken {token}")
    if result == 0:
        print_colored("✅ Token de ngrok configurado correctamente", Colors.GREEN)
        return True
    else:
        print_colored("❌ Error al configurar el token de ngrok", Colors.RED)
        return False

def select_version():
    """Permite al usuario seleccionar la versión de Minecraft"""
    print_colored("\n🎯 Selecciona la versión de Minecraft:", Colors.CYAN)
    
    versions = list(MINECRAFT_VERSIONS.keys())
    for i, version in enumerate(versions, 1):
        print(f"{i}. Minecraft {version}")
    
    while True:
        try:
            choice = int(input("\nElige una opción (número): "))
            if 1 <= choice <= len(versions):
                return versions[choice - 1]
            else:
                print_colored("❌ Opción inválida", Colors.RED)
        except ValueError:
            print_colored("❌ Por favor ingresa un número válido", Colors.RED)

def select_server_type(version):
    """Permite al usuario seleccionar el tipo de servidor"""
    print_colored(f"\n🔧 Tipos de servidor disponibles para Minecraft {version}:", Colors.CYAN)
    
    server_types = list(MINECRAFT_VERSIONS[version].keys())
    descriptions = {
        "vanilla": "Servidor oficial de Mojang (sin mods)",
        "paper": "Optimizado para rendimiento y plugins",
        "fabric": "Soporte para mods de Fabric",
        "forge": "Soporte para mods de Forge"
    }
    
    for i, server_type in enumerate(server_types, 1):
        print(f"{i}. {server_type.title()} - {descriptions[server_type]}")
    
    while True:
        try:
            choice = int(input("\nElige el tipo de servidor (número): "))
            if 1 <= choice <= len(server_types):
                return server_types[choice - 1]
            else:
                print_colored("❌ Opción inválida", Colors.RED)
        except ValueError:
            print_colored("❌ Por favor ingresa un número válido", Colors.RED)

def select_ngrok_region():
    """Permite al usuario seleccionar la región de ngrok"""
    print_colored("\n🌍 Selecciona la región de ngrok:", Colors.CYAN)
    
    regions = list(NGROK_REGIONS.keys())
    for i, (code, description) in enumerate(NGROK_REGIONS.items(), 1):
        print(f"{i}. {code} - {description}")
    
    while True:
        try:
            choice = int(input("\nElige una región (número): "))
            if 1 <= choice <= len(regions):
                return regions[choice - 1]
            else:
                print_colored("❌ Opción inválida", Colors.RED)
        except ValueError:
            print_colored("❌ Por favor ingresa un número válido", Colors.RED)

def download_file(url, filename):
    """Descarga un archivo con barra de progreso"""
    print_colored(f"📥 Descargando {filename}...", Colors.YELLOW)
    
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded = 0
        
        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\r📊 Progreso: {progress:.1f}%", end="")
        
        print(f"\n✅ {filename} descargado correctamente")
        return True
        
    except Exception as e:
        print_colored(f"❌ Error al descargar {filename}: {str(e)}", Colors.RED)
        return False

def setup_server_files(version, server_type):
    """Configura los archivos del servidor"""
    server_dir = "minecraft_server"
    if os.path.exists(server_dir):
        shutil.rmtree(server_dir)
    os.makedirs(server_dir)
    os.chdir(server_dir)
    
    # Descargar el archivo del servidor
    url = MINECRAFT_VERSIONS[version][server_type]
    
    if server_type == "forge":
        installer_name = f"forge-{version}-installer.jar"
        if download_file(url, installer_name):
            print_colored("🔧 Instalando Forge...", Colors.YELLOW)
            os.system(f"java -jar {installer_name} --installServer")
            
            # Buscar el archivo del servidor generado
            for file in os.listdir("."):
                if file.startswith("forge") and file.endswith(".jar") and "installer" not in file:
                    os.rename(file, "server.jar")
                    break
    else:
        if download_file(url, "server.jar"):
            print_colored("✅ Servidor descargado correctamente", Colors.GREEN)
    
    # Crear eula.txt
    with open("eula.txt", "w") as eula:
        eula.write("eula=true\n")
    
    # Crear server.properties básico
    server_properties = """
server-port=25565
gamemode=survival
difficulty=easy
spawn-protection=16
max-players=20
online-mode=true
white-list=false
enable-command-block=false
spawn-monsters=true
generate-structures=true
view-distance=10
motd=Servidor de Minecraft en GitHub Codespaces
""".strip()
    
    with open("server.properties", "w") as props:
        props.write(server_properties)
    
    # Crear script de inicio
    start_script = f"""#!/bin/bash
echo "🚀 Iniciando servidor de Minecraft {version} ({server_type})..."
java -Xmx2G -Xms1G -jar server.jar nogui
"""
    
    with open("start.sh", "w") as script:
        script.write(start_script)
    
    os.chmod("start.sh", 0o755)
    
    print_colored("✅ Archivos del servidor configurados", Colors.GREEN)

def start_ngrok_tunnel(region="us"):
    """Inicia el túnel de ngrok"""
    print_colored(f"🌐 Iniciando túnel ngrok en región: {region}", Colors.YELLOW)
    
    # Crear configuración de ngrok
    ngrok_config = f"""
version: "2"
tunnels:
  minecraft:
    proto: tcp
    addr: 25565
    region: {region}
"""
    
    with open("ngrok.yml", "w") as config:
        config.write(ngrok_config)
    
    # Iniciar ngrok en segundo plano
    ngrok_process = subprocess.Popen(
        ["ngrok", "tcp", "25565", "--region", region],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Esperar a que ngrok se inicie
    time.sleep(5)
    
    try:
        # Obtener la URL del túnel
        response = requests.get("http://localhost:4040/api/tunnels")
        if response.status_code == 200:
            tunnels = response.json()["tunnels"]
            if tunnels:
                public_url = tunnels[0]["public_url"]
                host, port = public_url.replace("tcp://", "").split(":")
                
                print_colored("\n" + "="*60, Colors.RED)
                print_colored("🎮 SERVIDOR DE MINECRAFT LISTO 🎮", Colors.RED + Colors.BOLD)
                print_colored("="*60, Colors.RED)
                print_colored(f"🌐 IP del servidor: {host}", Colors.RED + Colors.BOLD)
                print_colored(f"🔌 Puerto: {port}", Colors.RED + Colors.BOLD)
                print_colored("="*60, Colors.RED)
                print_colored("⚠️  Comparte esta IP con tus amigos para que se conecten", Colors.YELLOW)
                print_colored("="*60 + "\n", Colors.RED)
                
                return ngrok_process, host, port
    except Exception as e:
        print_colored(f"❌ Error al obtener la URL de ngrok: {e}", Colors.RED)
    
    return ngrok_process, None, None

def start_minecraft_server():
    """Inicia el servidor de Minecraft"""
    print_colored("🚀 Iniciando servidor de Minecraft...", Colors.GREEN)
    
    # Iniciar el servidor
    server_process = subprocess.Popen(
        ["java", "-Xmx2G", "-Xms1G", "-jar", "server.jar", "nogui"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )
    
    return server_process

def monitor_server(server_process):
    """Monitorea la salida del servidor"""
    print_colored("📊 Monitoreando servidor...", Colors.BLUE)
    
    try:
        for line in iter(server_process.stdout.readline, ''):
            if line:
                # Colorear diferentes tipos de mensajes
                if "ERROR" in line or "Exception" in line:
                    print_colored(line.strip(), Colors.RED)
                elif "WARN" in line:
                    print_colored(line.strip(), Colors.YELLOW)
                elif "joined the game" in line or "left the game" in line:
                    print_colored(line.strip(), Colors.GREEN)
                else:
                    print(line.strip())
                    
                # Detectar cuando el servidor está listo
                if "Done" in line and "For help, type" in line:
                    print_colored("\n✅ ¡Servidor completamente iniciado y listo para recibir conexiones!", Colors.GREEN + Colors.BOLD)
                    
    except KeyboardInterrupt:
        print_colored("\n🛑 Deteniendo servidor...", Colors.YELLOW)
        server_process.terminate()
        server_process.wait()

def create_server():
    """Función principal para crear el servidor"""
    print_banner()
    
    # Instalar dependencias
    install_dependencies()
    
    # Configurar ngrok
    if not setup_ngrok_token():
        return
    
    # Seleccionar versión y tipo de servidor
    version = select_version()
    server_type = select_server_type(version)
    region = select_ngrok_region()
    
    print_colored(f"\n🎯 Configuración seleccionada:", Colors.CYAN)
    print_colored(f"   📦 Versión: Minecraft {version}", Colors.WHITE)
    print_colored(f"   🔧 Tipo: {server_type.title()}", Colors.WHITE)
    print_colored(f"   🌍 Región: {NGROK_REGIONS[region]}", Colors.WHITE)
    
    input("\n⏸️  Presiona Enter para continuar...")
    
    # Configurar archivos del servidor
    setup_server_files(version, server_type)
    
    # Iniciar túnel ngrok
    ngrok_process, host, port = start_ngrok_tunnel(region)
    
    if host and port:
        # Iniciar servidor de Minecraft
        server_process = start_minecraft_server()
        
        try:
            # Monitorear el servidor
            monitor_server(server_process)
        except KeyboardInterrupt:
            print_colored("\n🛑 Cerrando servidor y túnel...", Colors.YELLOW)
        finally:
            # Limpiar procesos
            if server_process:
                server_process.terminate()
            if ngrok_process:
                ngrok_process.terminate()
    else:
        print_colored("❌ No se pudo establecer el túnel ngrok", Colors.RED)

def main_menu():
    """Menú principal"""
    setup_gitignore()
    
    while True:
        print_banner()
        print_colored("🎮 MENÚ PRINCIPAL", Colors.CYAN + Colors.BOLD)
        print_colored("─" * 40, Colors.CYAN)
        print("1. 🏗️  Crear Servidor")
        print("2. 📋 Ver Información")
        print("3. 🚪 Salir")
        print_colored("─" * 40, Colors.CYAN)
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "1":
            create_server()
        elif choice == "2":
            show_info()
        elif choice == "3":
            print_colored("👋 ¡Hasta luego!", Colors.GREEN)
            break
        else:
            print_colored("❌ Opción inválida", Colors.RED)
            time.sleep(1)

def show_info():
    """Muestra información sobre el script"""
    info = """
🎮 SERVIDOR DE MINECRAFT PARA GITHUB CODESPACES

📋 Características:
   • Soporte para múltiples versiones de Minecraft
   • Tipos de servidor: Vanilla, Paper, Fabric, Forge
   • Integración completa con ngrok
   • Configuración automática
   • Monitoreo en tiempo real

🔧 Tipos de servidor soportados:
   • Vanilla: Servidor oficial sin modificaciones
   • Paper: Optimizado para mejor rendimiento
   • Fabric: Soporte para mods de Fabric
   • Forge: Soporte para mods de Forge

🌍 Regiones de ngrok disponibles:
   • Asia/Pacífico, Australia, Europa, India
   • Japón, Sudamérica, Estados Unidos

⚠️  Requisitos:
   • GitHub Codespace o entorno Linux
   • Token de ngrok (gratis en ngrok.com)
   • Conexión a internet estable

📞 Soporte:
   • Creado para la comunidad de Minecraft
   • Compatible con GitHub Codespaces
"""
    print_colored(info, Colors.WHITE)
    input("\n⏸️  Presiona Enter para volver al menú...")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print_colored("\n\n👋 ¡Hasta luego!", Colors.GREEN)
    except Exception as e:
        print_colored(f"\n❌ Error inesperado: {str(e)}", Colors.RED)
