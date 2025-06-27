#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor de Minecraft para GitHub Codespaces con PlayIt
Autor: Asistente Claude
"""

import os
import sys
import json
import time
import shutil
import signal
import zipfile
import tarfile
import requests
import subprocess
import threading
from pathlib import Path

class MinecraftServer:
    def __init__(self):
        self.server_dir = Path("minecraft_server")
        self.config_file = Path("server_config.json")
        self.playit_process = None
        self.server_process = None
        
        # Versiones disponibles
        self.versions = {
            "vanilla": "Vanilla - Servidor oficial de Minecraft",
            "paper": "Paper - Optimizado para rendimiento",
            "forge": "Forge - Para mods de Forge",
            "fabric": "Fabric - Para mods de Fabric",
            "mohist": "Mohist - Forge + Bukkit plugins"
        }
        
        # URLs de descarga (estas se actualizarán según la versión seleccionada)
        self.download_urls = {
            "vanilla": "https://piston-data.mojang.com/v1/objects/{hash}/server.jar",
            "paper": "https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar",
            "forge": "https://maven.minecraftforge.net/net/minecraftforge/forge/{version}/forge-{version}-installer.jar",
            "fabric": "https://meta.fabricmc.net/v2/versions/loader/{mc_version}/{loader_version}/{installer_version}/server/jar",
            "mohist": "https://mohistmc.com/api/v2/projects/mohist/versions/{version}/builds/latest/download"
        }

    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_banner(self):
        """Imprime el banner del servidor"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                   SERVIDOR MINECRAFT                         ║
║                  GitHub Codespaces + PlayIt                  ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def install_dependencies(self):
        """Instala las dependencias necesarias"""
        print("📦 Instalando dependencias...")
        
        # Instalar Java si no está disponible
        if not shutil.which("java"):
            print("☕ Instalando Java...")
            os.system("sudo apt update && sudo apt install -y openjdk-17-jdk")
        
        print("✅ Dependencias instaladas correctamente")

    def get_playit_token(self):
        """Solicita el token de PlayIt al usuario"""
        print("\n🔑 Configuración de PlayIt")
        print("=" * 50)
        print("Para usar PlayIt necesitas:")
        print("1. Crear una cuenta en https://playit.gg/")
        print("2. Obtener tu token de acceso")
        print("3. Pegarlo aquí")
        print()
        
        token = input("Ingresa tu token de PlayIt: ").strip()
        if not token:
            print("❌ Token no puede estar vacío")
            return self.get_playit_token()
        
        return token

    def setup_playit(self, token):
        """Configura PlayIt con el token proporcionado"""
        print("🌐 Configurando PlayIt...")
        
        # Descargar PlayIt si no existe
        playit_path = Path("playit")
        if not playit_path.exists():
            print("📥 Descargando PlayIt...")
            try:
                # Detectar arquitectura
                arch_cmd = subprocess.run(["uname", "-m"], capture_output=True, text=True)
                arch = arch_cmd.stdout.strip()
                
                if arch == "x86_64":
                    playit_url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux_64"
                else:
                    playit_url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux"
                
                response = requests.get(playit_url)
                response.raise_for_status()
                
                with open(playit_path, "wb") as f:
                    f.write(response.content)
                
                os.chmod(playit_path, 0o755)
                print("✅ PlayIt descargado correctamente")
                
            except Exception as e:
                print(f"❌ Error descargando PlayIt: {e}")
                return False
        
        # Configurar PlayIt con el token
        try:
            # Crear directorio de configuración
            playit_config_dir = Path.home() / ".playit"
            playit_config_dir.mkdir(exist_ok=True)
            
            # Escribir token
            with open(playit_config_dir / "playit.toml", "w") as f:
                f.write(f'secret_key = "{token}"\n')
            
            print("✅ PlayIt configurado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando PlayIt: {e}")
            return False

    def select_version(self):
        """Permite al usuario seleccionar la versión de Minecraft"""
        print("\n🎮 Selecciona la versión de Minecraft")
        print("=" * 50)
        
        versions_list = list(self.versions.keys())
        for i, (key, desc) in enumerate(self.versions.items(), 1):
            print(f"{i}. {desc}")
        
        while True:
            try:
                choice = int(input(f"\nSelecciona una opción (1-{len(versions_list)}): "))
                if 1 <= choice <= len(versions_list):
                    selected = versions_list[choice - 1]
                    print(f"✅ Seleccionado: {self.versions[selected]}")
                    return selected
                else:
                    print(f"❌ Opción inválida. Ingresa un número entre 1 y {len(versions_list)}")
            except ValueError:
                print("❌ Por favor ingresa un número válido")

    def get_minecraft_version(self, server_type):
        """Solicita la versión específica de Minecraft"""
        print(f"\n📋 Versión de Minecraft para {server_type}")
        print("=" * 50)
        
        if server_type == "vanilla":
            print("Versiones populares: 1.20.4, 1.20.1, 1.19.4, 1.18.2")
        elif server_type == "paper":
            print("Versiones populares: 1.20.4, 1.20.1, 1.19.4, 1.18.2")
        elif server_type == "forge":
            print("Versiones populares: 1.20.1, 1.19.2, 1.18.2, 1.16.5")
        elif server_type == "fabric":
            print("Versiones populares: 1.20.4, 1.20.1, 1.19.4, 1.18.2")
        elif server_type == "mohist":
            print("Versiones populares: 1.20.1, 1.19.2, 1.18.2, 1.16.5")
        
        version = input("Ingresa la versión (ej: 1.20.4): ").strip()
        if not version:
            print("❌ La versión no puede estar vacía")
            return self.get_minecraft_version(server_type)
        
        return version

    def download_server(self, server_type, version):
        """Descarga el archivo del servidor"""
        print(f"\n📥 Descargando servidor {server_type} {version}...")
        
        self.server_dir.mkdir(exist_ok=True)
        server_jar = self.server_dir / "server.jar"
        
        try:
            if server_type == "vanilla":
                # Obtener información de la versión desde la API de Mojang
                manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
                manifest = requests.get(manifest_url).json()
                
                version_info = None
                for v in manifest["versions"]:
                    if v["id"] == version:
                        version_info = v
                        break
                
                if not version_info:
                    print(f"❌ Versión {version} no encontrada")
                    return False
                
                # Obtener URL del servidor
                version_data = requests.get(version_info["url"]).json()
                server_url = version_data["downloads"]["server"]["url"]
                
            elif server_type == "paper":
                # API de Paper
                builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
                builds = requests.get(builds_url).json()
                latest_build = builds["builds"][-1]["build"]
                server_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
                
            elif server_type == "fabric":
                # API de Fabric
                server_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/stable/server/jar"
                
            else:
                print(f"❌ Tipo de servidor {server_type} no implementado completamente")
                return False
            
            # Descargar archivo
            print("⬇️ Descargando archivo del servidor...")
            response = requests.get(server_url, stream=True)
            response.raise_for_status()
            
            with open(server_jar, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("✅ Servidor descargado correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error descargando servidor: {e}")
            return False

    def create_server_files(self):
        """Crea los archivos necesarios del servidor"""
        print("📝 Creando archivos de configuración...")
        
        # eula.txt
        eula_path = self.server_dir / "eula.txt"
        with open(eula_path, "w") as f:
            f.write("eula=true\n")
        
        # server.properties básico
        properties_path = self.server_dir / "server.properties"
        properties = """
# Minecraft server properties
server-port=25565
difficulty=easy
gamemode=survival
max-players=10
motd=Servidor Minecraft en GitHub Codespaces
online-mode=false
pvp=true
spawn-protection=16
view-distance=10
        """.strip()
        
        with open(properties_path, "w") as f:
            f.write(properties)
        
        print("✅ Archivos de configuración creados")

    def start_playit(self):
        """Inicia PlayIt en segundo plano"""
        print("🌐 Iniciando PlayIt...")
        
        try:
            self.playit_process = subprocess.Popen(
                ["./playit", "--stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Esperar a que PlayIt se inicie y mostrar la IP
            time.sleep(5)
            
            # Intentar obtener la información de conexión
            try:
                result = subprocess.run(
                    ["./playit", "status"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if "Address:" in result.stdout:
                    for line in result.stdout.split('\n'):
                        if "Address:" in line:
                            address = line.split("Address:")[1].strip()
                            print(f"🌍 IP del servidor: {address}")
                            print(f"🎮 Conecta usando: {address}")
                            break
                else:
                    print("🌐 PlayIt iniciado. Verifica tu panel de PlayIt para obtener la IP")
                    
            except subprocess.TimeoutExpired:
                print("🌐 PlayIt iniciado. Verifica tu panel de PlayIt para obtener la IP")
                
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando PlayIt: {e}")
            return False

    def start_server(self):
        """Inicia el servidor de Minecraft"""
        print("🚀 Iniciando servidor de Minecraft...")
        
        try:
            os.chdir(self.server_dir)
            
            # Comando para iniciar el servidor
            cmd = ["java", "-Xmx2G", "-Xms1G", "-jar", "server.jar", "nogui"]
            
            print("=" * 60)
            print("SERVIDOR MINECRAFT INICIADO")
            print("Presiona Ctrl+C para detener el servidor")
            print("=" * 60)
            
            self.server_process = subprocess.Popen(cmd)
            self.server_process.wait()
            
        except KeyboardInterrupt:
            print("\n🛑 Deteniendo servidor...")
            self.stop_server()
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")

    def stop_server(self):
        """Detiene el servidor y PlayIt"""
        if self.server_process:
            self.server_process.terminate()
            
        if self.playit_process:
            self.playit_process.terminate()
            
        print("✅ Servidor detenido")

    def main_menu(self):
        """Menú principal"""
        while True:
            self.clear_screen()
            self.print_banner()
            
            print("🎯 Menú Principal")
            print("=" * 30)
            print("1. Crear servidor")
            print("2. Iniciar servidor existente")
            print("3. Configurar PlayIt")
            print("4. Salir")
            
            choice = input("\nSelecciona una opción: ").strip()
            
            if choice == "1":
                self.create_server_menu()
            elif choice == "2":
                self.start_existing_server()
            elif choice == "3":
                self.configure_playit()
            elif choice == "4":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def create_server_menu(self):
        """Menú para crear servidor"""
        self.clear_screen()
        self.print_banner()
        
        # Instalar dependencias
        self.install_dependencies()
        
        # Configurar PlayIt
        token = self.get_playit_token()
        if not self.setup_playit(token):
            input("❌ Error configurando PlayIt. Presiona Enter para continuar...")
            return
        
        # Seleccionar tipo de servidor
        server_type = self.select_version()
        
        # Seleccionar versión
        version = self.get_minecraft_version(server_type)
        
        # Descargar servidor
        if not self.download_server(server_type, version):
            input("❌ Error descargando servidor. Presiona Enter para continuar...")
            return
        
        # Crear archivos
        self.create_server_files()
        
        # Guardar configuración
        config = {
            "server_type": server_type,
            "version": version,
            "playit_token": token
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print("\n✅ Servidor creado exitosamente!")
        
        # Preguntar si quiere iniciarlo
        start_now = input("¿Deseas iniciar el servidor ahora? (s/n): ").lower()
        if start_now in ['s', 'si', 'yes', 'y']:
            self.start_server_with_playit()
        else:
            input("Presiona Enter para volver al menú principal...")

    def start_existing_server(self):
        """Inicia un servidor existente"""
        if not self.server_dir.exists() or not self.config_file.exists():
            print("❌ No se encontró un servidor existente. Crea uno primero.")
            input("Presiona Enter para continuar...")
            return
        
        self.start_server_with_playit()

    def start_server_with_playit(self):
        """Inicia PlayIt y el servidor"""
        # Iniciar PlayIt
        if not self.start_playit():
            input("❌ Error iniciando PlayIt. Presiona Enter para continuar...")
            return
        
        print("\n⏳ Esperando a que PlayIt se estabilice...")
        time.sleep(3)
        
        # Iniciar servidor
        self.start_server()

    def configure_playit(self):
        """Configurar PlayIt manualmente"""
        self.clear_screen()
        self.print_banner()
        
        token = self.get_playit_token()
        if self.setup_playit(token):
            print("✅ PlayIt configurado correctamente")
        else:
            print("❌ Error configurando PlayIt")
        
        input("Presiona Enter para continuar...")

    def run(self):
        """Ejecuta la aplicación"""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
        finally:
            self.stop_server()

if __name__ == "__main__":
    server = MinecraftServer()
    server.run()
