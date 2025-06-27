#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import requests
import subprocess
import zipfile
import shutil
from pathlib import Path

class MinecraftServerManager:
    def __init__(self):
        self.config_file = "server_config.json"
        self.server_dir = "minecraft_server"
        self.versions = {
            "1.20.4": "https://piston-data.mojang.com/v1/objects/8f3112a1049751cc472ec13e397eade5336ca7ae/server.jar",
            "1.20.1": "https://piston-data.mojang.com/v1/objects/84194a2f286ef7c14ed7ce0090dba59902951553/server.jar",
            "1.19.4": "https://piston-data.mojang.com/v1/objects/8f3112a1049751cc472ec13e397eade5336ca7ae/server.jar",
            "1.18.2": "https://piston-data.mojang.com/v1/objects/c8f83c5655308435b3dcf03c06d9fe8740a77469/server.jar",
            "1.16.5": "https://piston-data.mojang.com/v1/objects/1b557e7b033b583cd9f66746b7a9ab1ec1673ced/server.jar"
        }
        
        self.server_types = {
            "vanilla": {
                "name": "Vanilla (Oficial de Mojang)",
                "description": "Servidor oficial sin modificaciones"
            },
            "paper": {
                "name": "Paper (Optimizado)",
                "description": "Servidor optimizado con plugins Bukkit/Spigot",
                "base": "vanilla"
            },
            "forge": {
                "name": "Forge (Mods)",
                "description": "Servidor para mods de Forge"
            },
            "fabric": {
                "name": "Fabric (Mods Ligeros)",
                "description": "Servidor para mods de Fabric"
            },
            "mohist": {
                "name": "Mohist (Híbrido)",
                "description": "Forge + Bukkit plugins",
                "base": "forge"
            }
        }
        
        self.ngrok_regions = {
            "us": "Estados Unidos (Ohio)",
            "us-cal-1": "Estados Unidos (California)",
            "eu": "Europa (Frankfurt)",
            "ap": "Asia/Pacífico (Singapore)",
            "au": "Australia (Sydney)",
            "jp": "Japón (Tokyo)",
            "sa": "Sudamérica (São Paulo)",
            "in": "India (Mumbai)"
        }

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        print("=" * 60)
        print("🎮 GESTOR DE SERVIDOR MINECRAFT - GITHUB CODESPACES 🎮")
        print("=" * 60)
        print()

    def setup_gitignore(self):
        gitignore_content = """
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

# Minecraft Server
minecraft_server/
server_config.json
*.jar
logs/
world/
world_nether/
world_the_end/
crash-reports/
banned-*.json
ops.json
whitelist.json
usercache.json
usernamecache.json
eula.txt

# Ngrok
ngrok
ngrok.yml
"""
        with open(".gitignore", "w") as f:
            f.write(gitignore_content.strip())

    def install_dependencies(self):
        print("📦 Instalando dependencias...")
        try:
            # Instalar Java si no está disponible
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt", "install", "-y", "openjdk-17-jdk", "wget", "unzip"], 
                         check=True, capture_output=True)
            
            # Descargar ngrok si no existe
            if not os.path.exists("ngrok"):
                print("🌐 Descargando ngrok...")
                ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
                subprocess.run(["wget", "-O", "ngrok.tgz", ngrok_url], check=True, capture_output=True)
                subprocess.run(["tar", "xzf", "ngrok.tgz"], check=True, capture_output=True)
                subprocess.run(["chmod", "+x", "ngrok"], check=True, capture_output=True)
                os.remove("ngrok.tgz")
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando dependencias: {e}")
            return False

    def select_version(self):
        self.clear_screen()
        self.print_header()
        print("🎯 SELECCIONAR VERSIÓN DE MINECRAFT")
        print("-" * 40)
        
        versions_list = list(self.versions.keys())
        for i, version in enumerate(versions_list, 1):
            print(f"{i}. Minecraft {version}")
        
        print(f"{len(versions_list) + 1}. Versión personalizada")
        print()
        
        while True:
            try:
                choice = input("Selecciona una opción: ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(versions_list):
                    return versions_list[choice_num - 1]
                elif choice_num == len(versions_list) + 1:
                    custom_version = input("Introduce la versión personalizada: ").strip()
                    return custom_version
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor, introduce un número válido")

    def select_server_type(self):
        self.clear_screen()
        self.print_header()
        print("⚙️ CREAR SERVIDOR - TIPO DE SERVIDOR")
        print("-" * 40)
        
        server_list = list(self.server_types.keys())
        for i, server_type in enumerate(server_list, 1):
            info = self.server_types[server_type]
            print(f"{i}. {info['name']}")
            print(f"   {info['description']}")
            if 'base' in info:
                print(f"   (Requiere instalar {info['base']} primero)")
            print()
        
        while True:
            try:
                choice = input("Selecciona el tipo de servidor: ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(server_list):
                    return server_list[choice_num - 1]
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor, introduce un número válido")

    def select_ngrok_region(self):
        self.clear_screen()
        self.print_header()
        print("🌍 SELECCIONAR REGIÓN DE NGROK")
        print("-" * 40)
        
        regions_list = list(self.ngrok_regions.keys())
        for i, region in enumerate(regions_list, 1):
            print(f"{i}. {region} - {self.ngrok_regions[region]}")
        
        print()
        while True:
            try:
                choice = input("Selecciona la región: ").strip()
                choice_num = int(choice)
                
                if 1 <= choice_num <= len(regions_list):
                    return regions_list[choice_num - 1]
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor, introduce un número válido")

    def download_server_jar(self, version, server_type):
        print(f"📥 Descargando servidor {server_type} para Minecraft {version}...")
        
        # Crear directorio del servidor
        Path(self.server_dir).mkdir(exist_ok=True)
        
        jar_path = os.path.join(self.server_dir, "server.jar")
        
        try:
            if server_type == "vanilla":
                if version in self.versions:
                    url = self.versions[version]
                else:
                    print(f"❌ Versión {version} no disponible")
                    return False
                    
            elif server_type == "paper":
                # Descargar Paper
                paper_api = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
                response = requests.get(paper_api)
                if response.status_code == 200:
                    builds = response.json()['builds']
                    latest_build = builds[-1]['build']
                    url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
                else:
                    print(f"❌ No se pudo obtener Paper para la versión {version}")
                    return False
                    
            elif server_type == "fabric":
                # Descargar Fabric
                fabric_api = f"https://meta.fabricmc.net/v2/versions/loader/{version}"
                response = requests.get(fabric_api)
                if response.status_code == 200:
                    loader_version = response.json()[0]['version']
                    installer_version = "0.11.2"  # Versión estable del instalador
                    url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
                else:
                    print(f"❌ No se pudo obtener Fabric para la versión {version}")
                    return False
                    
            elif server_type == "forge":
                print("⚠️ Forge requiere instalación manual. Descargando Vanilla por ahora...")
                if version in self.versions:
                    url = self.versions[version]
                else:
                    print(f"❌ Versión {version} no disponible")
                    return False
                    
            else:
                print(f"❌ Tipo de servidor {server_type} no soportado aún")
                return False
            
            # Descargar el archivo
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(jar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print("✅ Servidor descargado exitosamente")
                return True
            else:
                print(f"❌ Error descargando servidor: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def configure_server(self):
        # Crear server.properties
        server_properties = """
# Configuración del servidor Minecraft
server-port=25565
gamemode=survival
difficulty=easy
max-players=20
online-mode=false
enable-command-block=true
spawn-protection=0
motd=Servidor Minecraft en GitHub Codespaces
view-distance=10
"""
        
        properties_path = os.path.join(self.server_dir, "server.properties")
        with open(properties_path, "w") as f:
            f.write(server_properties.strip())
        
        # Aceptar EULA
        eula_path = os.path.join(self.server_dir, "eula.txt")
        with open(eula_path, "w") as f:
            f.write("eula=true\n")
        
        print("✅ Servidor configurado")

    def setup_ngrok(self, region):
        print("🌐 Configurando ngrok...")
        
        # Solicitar token de ngrok
        token = input("Introduce tu token de ngrok (obtén uno gratis en https://ngrok.com): ").strip()
        
        if not token:
            print("❌ Token de ngrok requerido")
            return False
        
        try:
            # Configurar ngrok
            subprocess.run(["./ngrok", "config", "add-authtoken", token], check=True)
            print("✅ Ngrok configurado")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error configurando ngrok")
            return False

    def start_server(self, region):
        print("🚀 Iniciando servidor...")
        
        # Cambiar al directorio del servidor
        os.chdir(self.server_dir)
        
        try:
            # Iniciar ngrok en segundo plano
            print("🌐 Iniciando túnel ngrok...")
            ngrok_cmd = [f"..{os.sep}ngrok", "tcp", "25565", "--region", region]
            ngrok_process = subprocess.Popen(ngrok_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Esperar un poco para que ngrok se inicie
            time.sleep(5)
            
            # Obtener la URL de ngrok
            try:
                response = requests.get("http://localhost:4040/api/tunnels")
                if response.status_code == 200:
                    tunnels = response.json()['tunnels']
                    if tunnels:
                        public_url = tunnels[0]['public_url']
                        host, port = public_url.replace('tcp://', '').split(':')
                        print(f"🌐 Servidor disponible en: {host}:{port}")
                        print("📋 Copia esta dirección para conectarte desde Minecraft")
            except:
                print("⚠️ No se pudo obtener la URL pública. Revisa ngrok manualmente.")
            
            # Iniciar servidor de Minecraft
            print("🎮 Iniciando Minecraft Server...")
            print("⚠️ El servidor se iniciará. Usa 'stop' para detenerlo.")
            print("-" * 50)
            
            java_cmd = ["java", "-Xmx2G", "-Xms1G", "-jar", "server.jar", "nogui"]
            subprocess.run(java_cmd)
            
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
        finally:
            # Limpiar procesos
            try:
                ngrok_process.terminate()
            except:
                pass
            os.chdir("..")

    def main_menu(self):
        while True:
            self.clear_screen()
            self.print_header()
            print("📋 MENÚ PRINCIPAL")
            print("-" * 30)
            print("1. 🆕 Crear Servidor")
            print("2. ▶️  Iniciar Servidor Existente")
            print("3. ⚙️  Gestionar Servidor")
            print("4. 🔧 Configuración")
            print("5. ❌ Salir")
            print()
            
            choice = input("Selecciona una opción: ").strip()
            
            if choice == "1":
                self.create_server_workflow()
            elif choice == "2":
                self.start_existing_server()
            elif choice == "3":
                self.manage_server()
            elif choice == "4":
                self.configuration_menu()
            elif choice == "5":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def create_server_workflow(self):
        print("🆕 Iniciando proceso de creación de servidor...")
        
        # Instalar dependencias
        if not self.install_dependencies():
            input("❌ Error instalando dependencias. Presiona Enter para continuar...")
            return
        
        # Seleccionar versión
        version = self.select_version()
        
        # Seleccionar tipo de servidor
        server_type = self.select_server_type()
        
        # Verificar dependencias del tipo de servidor
        if server_type in ["paper", "mohist"] and server_type == "paper":
            base_type = self.server_types[server_type].get("base", "vanilla")
            print(f"ℹ️ {server_type} se basa en {base_type}")
        
        # Seleccionar región de ngrok
        region = self.select_ngrok_region()
        
        # Descargar servidor
        if not self.download_server_jar(version, server_type):
            input("❌ Error descargando servidor. Presiona Enter para continuar...")
            return
        
        # Configurar servidor
        self.configure_server()
        
        # Configurar ngrok
        if not self.setup_ngrok(region):
            input("❌ Error configurando ngrok. Presiona Enter para continuar...")
            return
        
        # Guardar configuración
        config = {
            "version": version,
            "server_type": server_type,
            "region": region,
            "created": time.time()
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        # Preguntar si iniciar ahora
        start_now = input("\n¿Deseas iniciar el servidor ahora? (s/n): ").strip().lower()
        if start_now == 's':
            self.start_server(region)

    def start_existing_server(self):
        if not os.path.exists(self.config_file):
            print("❌ No hay servidor configurado. Crea uno primero.")
            input("Presiona Enter para continuar...")
            return
        
        with open(self.config_file, "r") as f:
            config = json.load(f)
        
        print(f"▶️ Iniciando servidor {config['server_type']} v{config['version']}")
        self.start_server(config['region'])

    def manage_server(self):
        print("⚙️ Gestión de servidor - Próximamente")
        input("Presiona Enter para continuar...")

    def configuration_menu(self):
        print("🔧 Configuración - Próximamente")
        input("Presiona Enter para continuar...")

def main():
    # Configurar gitignore
    manager = MinecraftServerManager()
    manager.setup_gitignore()
    
    print("🎮 Bienvenido al Gestor de Servidor Minecraft para GitHub Codespaces")
    print("📝 Asegúrate de tener una cuenta en ngrok.com para obtener tu token")
    input("Presiona Enter para continuar...")
    
    manager.main_menu()

if __name__ == "__main__":
    main()
