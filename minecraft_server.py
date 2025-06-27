#!Usa: python minecraft_server.py "en el terminal para iniciar el server".

import os
import sys
import json
import time
import requests
import subprocess
import zipfile
import shutil
import threading
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

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        print("=" * 65)
        print("🎮 SERVIDOR MINECRAFT CON PLAYIT - GITHUB CODESPACES 🎮")
        print("=" * 65)
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

# Playit
playit
playit.toml
"""
        with open(".gitignore", "w") as f:
            f.write(gitignore_content.strip())

    def install_dependencies(self):
        print("📦 Instalando dependencias...")
        try:
            # Instalar Java si no está disponible
            subprocess.run(["sudo", "apt", "update"], check=True, capture_output=True)
            subprocess.run(["sudo", "apt", "install", "-y", "openjdk-17-jdk", "wget", "curl"], 
                         check=True, capture_output=True)
            
            # Descargar playit si no existe
            if not os.path.exists("playit"):
                print("🌐 Descargando Playit...")
                playit_url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux"
                response = requests.get(playit_url)
                if response.status_code == 200:
                    with open("playit", "wb") as f:
                        f.write(response.content)
                    os.chmod("playit", 0o755)
                    print("✅ Playit descargado correctamente")
                else:
                    print("❌ Error descargando Playit")
                    return False
            
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error instalando dependencias: {e}")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
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
                print(f"   (Puedes instalar {info['base']} desde gestionar después)")
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

    def setup_playit(self):
        self.clear_screen()
        self.print_header()
        print("🌐 CONFIGURACIÓN DE PLAYIT")
        print("-" * 30)
        print()
        print("Para usar Playit necesitas:")
        print("1. 📱 Ir a: https://playit.gg")
        print("2. 🔑 Crear una cuenta gratuita")
        print("3. 📋 Copiar tu código de túnel")
        print()
        print("💡 El código de túnel se ve así: 'claim-XXXXXXXXXX'")
        print()
        
        tunnel_code = input("Ingresa tu código de túnel de Playit: ").strip()
        
        if not tunnel_code:
            print("❌ Código de túnel requerido")
            input("Presiona Enter para continuar...")
            return None
        
        if not tunnel_code.startswith("claim-"):
            print("⚠️ Advertencia: El código debería empezar con 'claim-'")
            confirm = input("¿Continuar de todos modos? (s/n): ").strip().lower()
            if confirm != 's':
                return None
        
        print("✅ Código de túnel guardado")
        return tunnel_code

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
                print("📄 Obteniendo Paper...")
                paper_api = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
                response = requests.get(paper_api)
                if response.status_code == 200:
                    builds = response.json()['builds']
                    latest_build = builds[-1]['build']
                    filename = f"paper-{version}-{latest_build}.jar"
                    url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/{filename}"
                else:
                    print(f"❌ No se pudo obtener Paper para la versión {version}")
                    return False
                    
            elif server_type == "fabric":
                # Descargar Fabric
                print("🧵 Obteniendo Fabric...")
                fabric_api = f"https://meta.fabricmc.net/v2/versions/loader/{version}"
                response = requests.get(fabric_api)
                if response.status_code == 200:
                    loader_version = response.json()[0]['version']
                    installer_version = "0.11.2"
                    url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader_version}/{installer_version}/server/jar"
                else:
                    print(f"❌ No se pudo obtener Fabric para la versión {version}")
                    return False
                    
            elif server_type == "forge":
                print("⚠️ Forge requiere instalación manual desde el menú de gestión.")
                print("📥 Descargando Vanilla como base...")
                if version in self.versions:
                    url = self.versions[version]
                else:
                    print(f"❌ Versión {version} no disponible")
                    return False
                    
            elif server_type == "mohist":
                print("⚠️ Mohist requiere instalar Forge primero desde el menú de gestión.")
                print("📥 Descargando Vanilla como base...")
                if version in self.versions:
                    url = self.versions[version]
                else:
                    print(f"❌ Versión {version} no disponible")
                    return False
                    
            else:
                print(f"❌ Tipo de servidor {server_type} no soportado")
                return False
            
            # Descargar el archivo
            print("⬇️ Descargando archivo del servidor...")
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(jar_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded / total_size) * 100
                                print(f"\r📊 Progreso: {percent:.1f}%", end="", flush=True)
                
                print("\n✅ Servidor descargado exitosamente")
                return True
            else:
                print(f"❌ Error descargando servidor: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def configure_server(self):
        print("⚙️ Configurando servidor...")
        
        # Crear server.properties
        server_properties = """# Configuración del servidor Minecraft
server-port=25565
gamemode=survival
difficulty=easy
max-players=20
online-mode=false
enable-command-block=true
spawn-protection=0
motd=\\u00A76Servidor Minecraft con Playit
view-distance=10
allow-flight=false
white-list=false
enforce-whitelist=false
pvp=true
generate-structures=true
op-permission-level=4
allow-nether=true
level-name=world
enable-query=false
enable-rcon=false
enable-status=true
"""
        
        properties_path = os.path.join(self.server_dir, "server.properties")
        with open(properties_path, "w") as f:
            f.write(server_properties.strip())
        
        # Aceptar EULA
        eula_path = os.path.join(self.server_dir, "eula.txt")
        with open(eula_path, "w") as f:
            f.write("eula=true\n")
        
        print("✅ Servidor configurado correctamente")

    def start_playit_tunnel(self, tunnel_code):
        """Inicia el túnel de Playit en segundo plano"""
        try:
            print("🌐 Iniciando túnel Playit...")
            
            # Comando para iniciar playit con el código de túnel
            cmd = ["./playit", "--secret_path", "playit.toml"]
            
            # Si es la primera vez, usar el código de claim
            if tunnel_code.startswith("claim-"):
                cmd = ["./playit", tunnel_code]
            
            # Iniciar proceso en segundo plano
            self.playit_process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Dar tiempo para que se establezca la conexión
            time.sleep(10)
            
            print("✅ Túnel Playit iniciado")
            print("🌐 Tu servidor será accesible a través de Playit")
            print("📱 Revisa tu panel en https://playit.gg para ver la IP pública")
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando Playit: {e}")
            return False

    def start_server(self, tunnel_code):
        print("🚀 INICIANDO SERVIDOR MINECRAFT")
        print("=" * 50)
        
        # Cambiar al directorio del servidor
        original_dir = os.getcwd()
        os.chdir(self.server_dir)
        
        try:
            # Iniciar túnel Playit
            playit_thread = threading.Thread(
                target=self.start_playit_tunnel, 
                args=(tunnel_code,)
            )
            playit_thread.daemon = True
            playit_thread.start()
            
            # Esperar un poco para que Playit se inicie
            time.sleep(5)
            
            print("\n🎮 INFORMACIÓN IMPORTANTE:")
            print("━" * 40)
            print("📱 Ve a https://playit.gg y entra a tu cuenta")
            print("🌐 En el panel verás la IP pública de tu servidor")
            print("📋 Comparte esa IP con tus amigos para jugar")
            print("⚠️  Usa 'stop' en la consola para detener el servidor")
            print("━" * 40)
            
            print("\n🚀 Iniciando Minecraft Server...")
            print("⏳ Esto puede tomar unos minutos la primera vez...")
            print("-" * 50)
            
            # Iniciar servidor de Minecraft
            java_cmd = [
                "java", 
                "-Xmx2G", 
                "-Xms1G", 
                "-XX:+UseG1GC",
                "-XX:+ParallelRefProcEnabled",
                "-XX:MaxGCPauseMillis=200",
                "-XX:+UnlockExperimentalVMOptions",
                "-XX:+DisableExplicitGC",
                "-XX:G1NewSizePercent=30",
                "-XX:G1MaxNewSizePercent=40",
                "-XX:G1HeapRegionSize=8M",
                "-XX:G1ReservePercent=20",
                "-XX:G1HeapWastePercent=5",
                "-XX:G1MixedGCCountTarget=4",
                "-XX:InitiatingHeapOccupancyPercent=15",
                "-XX:G1MixedGCLiveThresholdPercent=90",
                "-XX:G1RSetUpdatingPauseTimePercent=5",
                "-XX:SurvivorRatio=32",
                "-XX:+PerfDisableSharedMem",
                "-XX:MaxTenuringThreshold=1",
                "-jar", "server.jar", "nogui"
            ]
            subprocess.run(java_cmd)
            
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
        except Exception as e:
            print(f"❌ Error iniciando servidor: {e}")
        finally:
            # Limpiar procesos
            try:
                if hasattr(self, 'playit_process'):
                    self.playit_process.terminate()
                    print("🔌 Túnel Playit desconectado")
            except:
                pass
            os.chdir(original_dir)

    def main_menu(self):
        while True:
            self.clear_screen()
            self.print_header()
            print("📋 MENÚ PRINCIPAL")
            print("-" * 35)
            print("1. 🆕 Crear Servidor")
            print("2. ▶️  Iniciar Servidor Existente")
            print("3. ⚙️  Gestionar Servidor")
            print("4. 🔧 Configuración Playit")
            print("5. ℹ️  Información")
            print("6. ❌ Salir")
            print()
            
            choice = input("Selecciona una opción: ").strip()
            
            if choice == "1":
                self.create_server_workflow()
            elif choice == "2":
                self.start_existing_server()
            elif choice == "3":
                self.manage_server_menu()
            elif choice == "4":
                self.playit_configuration()
            elif choice == "5":
                self.show_info()
            elif choice == "6":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def create_server_workflow(self):
        print("🆕 CREANDO NUEVO SERVIDOR...")
        print("=" * 40)
        
        # Instalar dependencias
        if not self.install_dependencies():
            input("❌ Error instalando dependencias. Presiona Enter para continuar...")
            return
        
        # Seleccionar versión
        version = self.select_version()
        
        # Seleccionar tipo de servidor
        server_type = self.select_server_type()
        
        # Mostrar información sobre dependencias
        if server_type in ["paper", "mohist"]:
            base_type = self.server_types[server_type].get("base")
            if base_type:
                print(f"ℹ️ Nota: Puedes instalar {server_type} después de instalar {base_type} desde el menú de gestión")
        
        # Configurar Playit
        tunnel_code = self.setup_playit()
        if not tunnel_code:
            input("❌ Configuración de Playit cancelada. Presiona Enter para continuar...")
            return
        
        # Descargar servidor
        if not self.download_server_jar(version, server_type):
            input("❌ Error descargando servidor. Presiona Enter para continuar...")
            return
        
        # Configurar servidor
        self.configure_server()
        
        # Guardar configuración
        config = {
            "version": version,
            "server_type": server_type,
            "tunnel_code": tunnel_code,
            "created": time.time()
        }
        
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
        
        print("\n✅ ¡Servidor creado exitosamente!")
        print("=" * 40)
        
        # Preguntar si iniciar ahora
        start_now = input("\n¿Deseas iniciar el servidor ahora? (s/n): ").strip().lower()
        if start_now == 's':
            self.start_server(tunnel_code)

    def start_existing_server(self):
        if not os.path.exists(self.config_file):
            print("❌ No hay servidor configurado.")
            print("💡 Crea uno primero usando la opción 'Crear Servidor'")
            input("Presiona Enter para continuar...")
            return
        
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
            
            print(f"▶️ Iniciando servidor {config['server_type']} v{config['version']}")
            self.start_server(config['tunnel_code'])
        except Exception as e:
            print(f"❌ Error cargando configuración: {e}")
            input("Presiona Enter para continuar...")

    def manage_server_menu(self):
        while True:
            self.clear_screen()
            self.print_header()
            print("⚙️ GESTIONAR SERVIDOR")
            print("-" * 30)
            print("1. 📊 Estado del Servidor")
            print("2. 🔧 Instalar Mohist (después de Forge)")
            print("3. 📄 Instalar Paper (después de Vanilla)")
            print("4. 🧵 Instalar Purpur (después de Fabric)")
            print("5. 🗑️  Eliminar Servidor")
            print("6. 🔙 Volver al Menú Principal")
            print()
            
            choice = input("Selecciona una opción: ").strip()
            
            if choice == "1":
                self.show_server_status()
            elif choice == "2":
                self.install_mohist()
            elif choice == "3":
                self.install_paper()
            elif choice == "4":
                self.install_purpur()
            elif choice == "5":
                self.delete_server()
            elif choice == "6":
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")

    def show_server_status(self):
        self.clear_screen()
        self.print_header()
        print("📊 ESTADO DEL SERVIDOR")
        print("-" * 30)
        
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                config = json.load(f)
            
            print(f"✅ Servidor configurado:")
            print(f"   📦 Tipo: {config['server_type']}")
            print(f"   🎯 Versión: {config['version']}")
            print(f"   📅 Creado: {time.ctime(config['created'])}")
            
            if os.path.exists(self.server_dir):
                print(f"   📁 Directorio: ✅ Existente")
                if os.path.exists(os.path.join(self.server_dir, "server.jar")):
                    print(f"   ☕ JAR: ✅ Presente")
                else:
                    print(f"   ☕ JAR: ❌ Faltante")
            else:
                print(f"   📁 Directorio: ❌ Faltante")
                
        else:
            print("❌ No hay servidor configurado")
        
        input("\nPresiona Enter para continuar...")

    def install_mohist(self):
        print("🔥 Instalando Mohist...")
        print("⚠️ Esta función estará disponible próximamente")
        input("Presiona Enter para continuar...")

    def install_paper(self):
        print("📄 Instalando Paper...")
        print("⚠️ Esta función estará disponible próximamente")
        input("Presiona Enter para continuar...")

    def install_purpur(self):
        print("💜 Instalando Purpur...")
        print("⚠️ Esta función estará disponible próximamente")
        input("Presiona Enter para continuar...")

    def delete_server(self):
        print("🗑️ ELIMINAR SERVIDOR")
        print("-" * 25)
        print("⚠️ Esta acción eliminará todos los archivos del servidor")
        confirm = input("¿Estás seguro? Escribe 'ELIMINAR' para confirmar: ").strip()
        
        if confirm == "ELIMINAR":
            try:
                if os.path.exists(self.server_dir):
                    shutil.rmtree(self.server_dir)
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                print("✅ Servidor eliminado correctamente")
            except Exception as e:
                print(f"❌ Error eliminando servidor: {e}")
        else:
            print("❌ Eliminación cancelada")
        
        input("Presiona Enter para continuar...")

    def playit_configuration(self):
        self.clear_screen()
        self.print_header()
        print("🔧 CONFIGURACIÓN PLAYIT")
        print("-" * 30)
        print("1. 🔑 Cambiar código de túnel")
        print("2. 📱 Abrir panel de Playit")
        print("3. ❓ Ayuda con Playit")
        print("4. 🔙 Volver")
        print()
        
        choice = input("Selecciona una opción: ").strip()
        
        if choice == "1":
            new_code = self.setup_playit()
            if new_code and os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                config["tunnel_code"] = new_code
                with open(self.config_file, "w") as f:
                    json.dump(config, f, indent=2)
                print("✅ Código actualizado")
            input("Presiona Enter para continuar...")
        elif choice == "2":
            print("🌐 Abre tu navegador y ve a: https://playit.gg")
            input("Presiona Enter para continuar...")
        elif choice == "3":
            self.show_playit_help()
        elif choice == "4":
            return
        else:
            print("❌ Opción inválida")
            input("Presiona Enter para continuar...")

    def show_playit_help(self):
        self.clear_screen()
        self.print_header()
        print("❓ AYUDA CON PLAYIT")
        print("-" * 25)
        print()
        print("🔗 ¿Qué es Playit?")
        print("   Playit es un servicio que crea túneles para hacer")
        print("   tu servidor accesible desde internet de forma gratuita.")
        print()
        print("📱 ¿Cómo obtener un código de túnel?")
        print("   1. Ve a https://playit.gg")
        print("   2. Crea una cuenta gratuita")
        print("   3. Haz clic en 'Create Tunnel'")
        print("   4. Selecciona 'Minecraft Java Edition'")
        print("   5. Copia el código que empieza con 'claim-'")
        print()
        print("🌐 ¿Cómo conectarse al servidor?")
        print("   1. Inicia tu servidor con este script")
        print("   2. Ve a tu panel en playit.gg")
        print("   3. Verás la IP pública (ej: example.playit.gg)")
        print("   4. Úsala en Minecraft para conectarte")
        print()
        print("💡 Consejos:")
        print("   • Playit es gratuito pero tiene límites de ancho de banda")
        print("   • La IP puede cambiar si reinicias el túnel")
        print("   • Guarda tu código de túnel para reutilizarlo")
        print()
        input("Presiona Enter para continuar...")

    def show_info(self):
        self.clear_screen()
        self.print_header()
        print("ℹ️ INFORMACIÓN DEL SISTEMA")
        print("-" * 35)
        print()
        print("📋 Versiones Disponibles:")
        for version in self.versions.keys():
            print(f"   • Minecraft {version}")
        print()
        print("⚙️ Tipos de Servidor:")
        print("   • Vanilla - Servidor oficial")
        print("   • Paper - Optimizado + plugins")
        print("   • Forge - Mods de Forge")
        print("   • Fabric - Mods ligeros")
        print("   • Mohist - Forge + Bukkit (instalar después)")
        print()
        print("🌐 Características:")
        print("   • Integración completa con Playit")
        print("   • Configuración automática")
        print("   • Soporte para GitHub Codespaces")
        print("   • Gestión de dependências")
        print()
        print("🔗 Enlaces útiles:")
        print("   • Playit: https://playit.gg")
        print("   • Minecraft: https://minecraft.net")
        print()
        input("Presiona Enter para continuar...")

def main():
    # Configurar gitignore
    manager = MinecraftServerManager()
    manager.setup_gitignore()
    
    manager.clear_screen()
    manager.print_header()
    print("🎮 ¡Bienvenido al Gestor de Servidor Minecraft con Playit!")
    print()
    print("📝 Instrucciones rápidas:")
    print("   1. Ve a https://playit.gg y crea una cuenta")
    print("   2. Crea un túnel para Minecraft Java Edition")
    print("   3. Copia tu código (claim-XXXXXXXXXX)")
    print("   4. ¡Usa este script para configurar todo automáticamente!")
    print()
    print("🚀 Características:")
    print("   • Soporte completo para Playit")
    print("   • Instalación automática de dependencias")
    print("   • Múltiples tipos de servidor (Vanilla, Paper, Forge, Fabric)")
    print("   • Configuración automática optimizada")
    print("   • Compatible con GitHub Codespaces")
    print()
    input("Presiona Enter para continuar...")
    
    manager.main_menu()

if __name__ == "__main__":
    main()
