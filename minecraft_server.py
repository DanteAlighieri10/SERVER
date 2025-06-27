#!/usr/bin/env python3
"""
Minecraft Server Manager para GitHub Codespaces
Administrador automático de servidores de Minecraft con soporte para múltiples tipos
"""

import os
import sys
import json
import time
import glob
import base64
import shutil
import requests
import zipfile
import subprocess
from pathlib import Path

class MinecraftServerManager:
    def __init__(self):
        self.server_dir = "./minecraft_server"
        self.config_file = "server_config.json"
        self.java_xmx = "2G"  # Memoria para el servidor
        
        # Versiones de Minecraft soportadas
        self.minecraft_versions = {
            "1.20.4": "1.20.4",
            "1.20.1": "1.20.1", 
            "1.19.4": "1.19.4",
            "1.19.2": "1.19.2",
            "1.18.2": "1.18.2",
            "1.17.1": "1.17.1",
            "1.16.5": "1.16.5"
        }
        
        # Tipos de servidor disponibles
        self.server_types = {
            "vanilla": "Servidor Vanilla oficial de Minecraft",
            "paper": "Servidor Paper (Optimizado, plugins Bukkit/Spigot)",
            "fabric": "Servidor Fabric (Mods de Fabric)",
            "forge": "Servidor Forge (Mods de Forge)",
            "mohist": "Servidor Mohist (Forge + Bukkit plugins)"
        }
        
        # Regiones de ngrok
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
        
        self.setup_gitignore()
        
    def setup_gitignore(self):
        """Configura el archivo .gitignore"""
        if not os.path.exists("./.gitignore"):
            gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# Minecraft Server
/minecraft_server/
/servidor_minecraft/
/servers/
*.jar
server.properties
eula.txt
logs/
world/
world_nether/
world_the_end/
*.log
banned-*.json
ops.json
whitelist.json
usercache.json
usernamecache.json

# Ngrok
ngrok
ngrok.exe
ngrok.yml

# Configuración
server_config.json
configuracion.json
configuration.json

# Otros
*.txt
*.output
*.msp
work_area*/
bkdir/
vendor/
composer.*
tailscale-cs/
thanos/
"""
            with open(".gitignore", 'w') as f:
                f.write(gitignore_content.strip())
    
    def clear_screen(self):
        """Limpia la pantalla"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def print_header(self):
        """Imprime el header del programa"""
        self.clear_screen()
        print("=" * 60)
        print("🎮 MINECRAFT SERVER MANAGER - GITHUB CODESPACES")
        print("=" * 60)
        print()
    
    def install_java(self):
        """Instala Java si no está disponible"""
        try:
            result = subprocess.run(['java', '-version'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Java ya está instalado")
                return True
        except FileNotFoundError:
            pass
            
        print("☕ Instalando Java...")
        try:
            subprocess.run(['sudo', 'apt', 'update'], check=True, capture_output=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'openjdk-17-jdk'], check=True, capture_output=True)
            print("✅ Java instalado correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error instalando Java")
            return False
    
    def download_file(self, url, filename):
        """Descarga un archivo desde una URL"""
        print(f"📥 Descargando {filename}...")
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded / total_size) * 100
                            print(f"\r📥 Progreso: {percent:.1f}%", end='', flush=True)
            
            print(f"\n✅ {filename} descargado correctamente")
            return True
        except Exception as e:
            print(f"\n❌ Error descargando {filename}: {e}")
            return False
    
    def get_vanilla_download_url(self, version):
        """Obtiene la URL de descarga del servidor vanilla"""
        try:
            # Obtener información de la versión
            version_manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
            response = requests.get(version_manifest_url)
            manifest = response.json()
            
            version_info = None
            for v in manifest['versions']:
                if v['id'] == version:
                    version_info = v
                    break
            
            if not version_info:
                return None
                
            # Obtener URL del servidor
            version_details_response = requests.get(version_info['url'])
            version_details = version_details_response.json()
            
            if 'downloads' in version_details and 'server' in version_details['downloads']:
                return version_details['downloads']['server']['url']
                
        except Exception as e:
            print(f"❌ Error obteniendo URL de descarga: {e}")
        
        return None
    
    def get_paper_download_url(self, version):
        """Obtiene la URL de descarga del servidor Paper"""
        try:
            # API de Paper
            api_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                builds = response.json()
                if builds['builds']:
                    latest_build = builds['builds'][-1]
                    build_number = latest_build['build']
                    jar_name = latest_build['downloads']['application']['name']
                    
                    download_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build_number}/downloads/{jar_name}"
                    return download_url
        except Exception as e:
            print(f"❌ Error obteniendo URL de Paper: {e}")
        
        return None
    
    def get_fabric_download_url(self, version):
        """Obtiene la URL de descarga del servidor Fabric"""
        try:
            # API de Fabric
            api_url = "https://meta.fabricmc.net/v2/versions/loader"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                loaders = response.json()
                if loaders:
                    latest_loader = loaders[0]['version']
                    installer_url = f"https://meta.fabricmc.net/v2/versions/loader/{version}/{latest_loader}/server/jar"
                    return installer_url
        except Exception as e:
            print(f"❌ Error obteniendo URL de Fabric: {e}")
        
        return None
    
    def download_server(self, server_type, version):
        """Descarga el archivo del servidor según el tipo"""
        if not os.path.exists(self.server_dir):
            os.makedirs(self.server_dir)
        
        os.chdir(self.server_dir)
        
        server_jar = f"{server_type}-{version}.jar"
        
        if server_type == "vanilla":
            url = self.get_vanilla_download_url(version)
            if url:
                return self.download_file(url, server_jar)
                
        elif server_type == "paper":
            url = self.get_paper_download_url(version)
            if url:
                return self.download_file(url, server_jar)
                
        elif server_type == "fabric":
            url = self.get_fabric_download_url(version)
            if url:
                return self.download_file(url, server_jar)
                
        elif server_type == "forge":
            print("🔨 Para Forge, necesitas descargar el instalador manualmente desde:")
            print(f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html")
            return False
            
        elif server_type == "mohist":
            print("🔨 Para Mohist, necesitas descargar desde:")
            print(f"https://mohistmc.com/download/{version}")
            return False
        
        print(f"❌ No se pudo obtener la URL de descarga para {server_type} {version}")
        return False
    
    def create_server_properties(self):
        """Crea el archivo server.properties"""
        properties_content = """
#Minecraft server properties
enable-jmx-monitoring=false
rcon.port=25575
level-seed=
gamemode=survival
enable-command-block=false
enable-query=false
generator-settings={}
level-name=world
motd=Servidor Minecraft en GitHub Codespaces
query.port=25565
pvp=true
generate-structures=true
difficulty=easy
network-compression-threshold=256
max-tick-time=60000
require-resource-pack=false
use-native-transport=true
max-players=20
online-mode=false
enable-status=true
allow-flight=false
broadcast-rcon-to-ops=true
view-distance=10
server-ip=
resource-pack-prompt=
allow-nether=true
server-port=25565
enable-rcon=false
sync-chunk-writes=true
op-permission-level=4
prevent-proxy-connections=false
hide-online-players=false
resource-pack=
entity-broadcast-range-percentage=100
simulation-distance=10
rcon.password=
player-idle-timeout=0
debug=false
force-gamemode=false
rate-limit=0
hardcore=false
white-list=false
broadcast-console-to-ops=true
spawn-npcs=true
spawn-animals=true
snooper-enabled=true
function-permission-level=2
level-type=minecraft\\:normal
text-filtering-config=
spawn-monsters=true
enforce-whitelist=false
spawn-protection=16
resource-pack-sha1=
max-world-size=29999984
""".strip()
        
        with open("server.properties", 'w') as f:
            f.write(properties_content)
        
        print("✅ server.properties creado")
    
    def accept_eula(self):
        """Acepta el EULA de Minecraft"""
        eula_content = """#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://account.mojang.com/documents/minecraft_eula).
#{}
eula=true
""".format(time.strftime('%c'))
        
        with open("eula.txt", 'w') as f:
            f.write(eula_content)
        
        print("✅ EULA aceptado")
    
    def create_start_script(self, server_type, version):
        """Crea el script de inicio del servidor"""
        jar_files = glob.glob("*.jar")
        if not jar_files:
            print("❌ No se encontró el archivo JAR del servidor")
            return False
        
        server_jar = jar_files[0]
        
        start_script_content = f"""#!/bin/bash
echo "🎮 Iniciando servidor Minecraft {server_type} {version}..."
echo "📊 Memoria asignada: {self.java_xmx}"
echo "🔧 Archivo JAR: {server_jar}"
echo ""

java -Xmx{self.java_xmx} -Xms1G -jar {server_jar} nogui
"""
        
        with open("start_server.sh", 'w') as f:
            f.write(start_script_content)
        
        os.chmod("start_server.sh", 0o755)
        print("✅ Script de inicio creado")
        return True
    
    def install_ngrok(self):
        """Instala ngrok para exponer el servidor"""
        if os.path.exists("./ngrok"):
            print("✅ ngrok ya está instalado")
            return True
            
        print("🌐 Instalando ngrok...")
        try:
            # Descargar ngrok
            ngrok_url = "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz"
            if self.download_file(ngrok_url, "ngrok.tgz"):
                # Extraer ngrok
                subprocess.run(['tar', '-xzf', 'ngrok.tgz'], check=True)
                os.remove("ngrok.tgz")
                os.chmod("ngrok", 0o755)
                print("✅ ngrok instalado correctamente")
                return True
        except Exception as e:
            print(f"❌ Error instalando ngrok: {e}")
        
        return False
    
    def setup_ngrok(self, region="us"):
        """Configura ngrok"""
        if not os.path.exists("./ngrok"):
            if not self.install_ngrok():
                return False
        
        print(f"🌐 Configurando ngrok en región: {region}")
        
        # Crear archivo de configuración de ngrok
        ngrok_config = f"""
version: "2"
region: {region}
tunnels:
  minecraft:
    proto: tcp
    addr: 25565
"""
        
        with open("ngrok.yml", 'w') as f:
            f.write(ngrok_config)
        
        print("✅ ngrok configurado")
        return True
    
    def start_ngrok(self):
        """Inicia ngrok en segundo plano"""
        try:
            print("🌐 Iniciando túnel ngrok...")
            subprocess.Popen(['./ngrok', 'start', '--config', 'ngrok.yml', 'minecraft'], 
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Esperar un poco para que ngrok se inicie
            time.sleep(5)
            
            # Obtener la URL pública
            max_attempts = 10
            for attempt in range(max_attempts):
                try:
                    response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
                    if response.status_code == 200:
                        tunnels = response.json()
                        if tunnels['tunnels']:
                            public_url = tunnels['tunnels'][0]['public_url']
                            host, port = public_url.replace('tcp://', '').split(':')
                            server_ip = f"{host}:{port}"
                            
                            print(f"🌐 Servidor disponible en: {server_ip}")
                            
                            # Crear archivo con la IP del servidor
                            self.save_server_ip(server_ip, host, port)
                            return True
                    
                    time.sleep(1)
                    
                except requests.exceptions.RequestException:
                    if attempt < max_attempts - 1:
                        time.sleep(1)
                        continue
                    else:
                        break
                
            print("🌐 ngrok iniciado (verifica en http://localhost:4040 para la URL)")
            print("⏰ Intentando obtener la IP automáticamente...")
            
            # Intentar obtener la IP después de un poco más de tiempo
            time.sleep(3)
            self.get_and_save_ngrok_ip()
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando ngrok: {e}")
            return False
    
    def get_and_save_ngrok_ip(self):
        """Obtiene y guarda la IP de ngrok después del inicio"""
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels['tunnels']:
                    public_url = tunnels['tunnels'][0]['public_url']
                    host, port = public_url.replace('tcp://', '').split(':')
                    server_ip = f"{host}:{port}"
                    
                    print(f"✅ IP del servidor obtenida: {server_ip}")
                    self.save_server_ip(server_ip, host, port)
                    return True
        except Exception as e:
            print(f"⚠️  No se pudo obtener la IP automáticamente: {e}")
            print("💡 Puedes verificar manualmente en http://localhost:4040")
        
        return False
    
    def save_server_ip(self, server_ip, host, port):
        """Guarda la IP del servidor en archivos de texto"""
        try:
            # Archivo principal con la IP completa
            with open("server_ip.txt", 'w') as f:
                f.write(f"🎮 INFORMACIÓN DEL SERVIDOR MINECRAFT\n")
                f.write(f"=" * 40 + "\n\n")
                f.write(f"📍 IP del Servidor: {server_ip}\n")
                f.write(f"🌐 Host: {host}\n")
                f.write(f"🔌 Puerto: {port}\n\n")
                f.write(f"📅 Generado: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"💡 INSTRUCCIONES PARA CONECTARSE:\n")
                f.write(f"   1. Abre Minecraft\n")
                f.write(f"   2. Ve a 'Multijugador'\n")
                f.write(f"   3. Haz clic en 'Agregar servidor'\n")
                f.write(f"   4. Ingresa la IP: {server_ip}\n")
                f.write(f"   5. ¡Conecta y disfruta!\n\n")
                f.write(f"⚠️  IMPORTANTE:\n")
                f.write(f"   - Esta IP es temporal y cambia cada vez que reinicias ngrok\n")
                f.write(f"   - El servidor debe estar ejecutándose para conectarse\n")
                f.write(f"   - Panel de control de ngrok: http://localhost:4040\n")
            
            # Archivo simple solo con la IP
            with open("ip.txt", 'w') as f:
                f.write(server_ip)
            
            # Archivo JSON para uso programático
            ip_data = {
                "server_ip": server_ip,
                "host": host,
                "port": port,
                "generated_at": time.strftime('%Y-%m-%d %H:%M:%S'),
                "ngrok_dashboard": "http://localhost:4040"
            }
            
            with open("server_info.json", 'w') as f:
                json.dump(ip_data, f, indent=2)
            
            print(f"💾 IP guardada en:")
            print(f"   📄 server_ip.txt (información completa)")
            print(f"   📄 ip.txt (solo la IP)")
            print(f"   📄 server_info.json (formato JSON)")
            
        except Exception as e:
            print(f"⚠️  Error guardando la IP: {e}")
    
    def create_ip_file_manually(self):
        """Permite crear manualmente el archivo de IP si ngrok no funcionó automáticamente"""
        print("📝 CREAR ARCHIVO DE IP MANUALMENTE")
        print("-" * 35)
        print("Si ngrok no pudo obtener la IP automáticamente,")
        print("puedes ingresarla manualmente aquí.")
        print()
        
        # Verificar si ngrok está corriendo
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=2)
            if response.status_code == 200:
                tunnels = response.json()
                if tunnels['tunnels']:
                    public_url = tunnels['tunnels'][0]['public_url']
                    host, port = public_url.replace('tcp://', '').split(':')
                    server_ip = f"{host}:{port}"
                    
                    print(f"✅ IP encontrada automáticamente: {server_ip}")
                    self.save_server_ip(server_ip, host, port)
                    input("Presiona Enter para continuar...")
                    return
        except:
            pass
        
        print("🌐 Ve a http://localhost:4040 para ver tu túnel ngrok")
        print("📋 Copia la dirección TCP (ejemplo: 0.tcp.ngrok.io:12345)")
        print()
        
        server_ip = input("Ingresa la IP del servidor (host:puerto): ").strip()
        
        if server_ip and ':' in server_ip:
            try:
                host, port = server_ip.split(':')
                self.save_server_ip(server_ip, host, port)
                print("✅ Archivo de IP creado correctamente")
            except:
                print("❌ Formato de IP inválido")
        else:
            print("❌ Formato de IP inválido. Debe ser host:puerto")
        
        input("Presiona Enter para continuar...")
    
    def show_main_menu(self):
        """Muestra el menú principal"""
        while True:
            self.print_header()
            print("🎯 MENÚ PRINCIPAL")
            print("-" * 30)
            print("1. 🆕 Crear nuevo servidor")
            print("2. ▶️  Iniciar servidor existente")
            print("3. ⚙️  Gestionar servidor")
            print("4. 🌐 Configurar ngrok")
            print("5. ❌ Salir")
            print()
            
            choice = input("Selecciona una opción (1-5): ").strip()
            
            if choice == "1":
                self.create_server_menu()
            elif choice == "2":
                self.start_existing_server()
            elif choice == "3":
                self.manage_server_menu()
            elif choice == "4":
                self.configure_ngrok_menu()
            elif choice == "5":
                print("👋 ¡Hasta luego!")
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")
    
    def create_server_menu(self):
        """Menú para crear un nuevo servidor"""
        self.print_header()
        print("🆕 CREAR NUEVO SERVIDOR")
        print("-" * 30)
        
        # Seleccionar versión
        print("📋 Versiones disponibles:")
        versions = list(self.minecraft_versions.keys())
        for i, version in enumerate(versions, 1):
            print(f"{i}. Minecraft {version}")
        print()
        
        while True:
            try:
                version_choice = int(input(f"Selecciona una versión (1-{len(versions)}): "))
                if 1 <= version_choice <= len(versions):
                    selected_version = versions[version_choice - 1]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor ingresa un número")
        
        # Seleccionar tipo de servidor
        print(f"\n🎮 Tipos de servidor para Minecraft {selected_version}:")
        server_types = list(self.server_types.keys())
        for i, server_type in enumerate(server_types, 1):
            print(f"{i}. {server_type.title()} - {self.server_types[server_type]}")
        print()
        
        while True:
            try:
                type_choice = int(input(f"Selecciona un tipo (1-{len(server_types)}): "))
                if 1 <= type_choice <= len(server_types):
                    selected_type = server_types[type_choice - 1]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor ingresa un número")
        
        # Confirmar selección
        print(f"\n✅ Configuración seleccionada:")
        print(f"   🎮 Versión: Minecraft {selected_version}")
        print(f"   🔧 Tipo: {selected_type.title()}")
        print(f"   💾 Directorio: {self.server_dir}")
        print()
        
        confirm = input("¿Continuar con la instalación? (s/N): ").lower().strip()
        if confirm not in ['s', 'si', 'y', 'yes']:
            return
        
        # Crear servidor
        self.create_server(selected_type, selected_version)
    
    def create_server(self, server_type, version):
        """Crea y configura un nuevo servidor"""
        print(f"\n🚀 Creando servidor {server_type} {version}...")
        
        # Instalar Java
        if not self.install_java():
            print("❌ No se pudo instalar Java")
            input("Presiona Enter para continuar...")
            return
        
        # Limpiar directorio anterior si existe
        if os.path.exists(self.server_dir):
            shutil.rmtree(self.server_dir)
        
        # Descargar servidor
        if not self.download_server(server_type, version):
            print("❌ No se pudo descargar el servidor")
            input("Presiona Enter para continuar...")
            return
        
        # Configurar servidor
        self.accept_eula()
        self.create_server_properties()
        
        if not self.create_start_script(server_type, version):
            print("❌ No se pudo crear el script de inicio")
            input("Presiona Enter para continuar...")
            return
        
        # Guardar configuración
        config = {
            "server_type": server_type,
            "version": version,
            "created_at": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        os.chdir("..")
        
        print(f"\n🎉 ¡Servidor {server_type} {version} creado exitosamente!")
        print(f"📁 Ubicación: {os.path.abspath(self.server_dir)}")
        print("\n¿Qué deseas hacer ahora?")
        print("1. ▶️  Iniciar servidor")
        print("2. 🌐 Configurar ngrok y luego iniciar")
        print("3. 🔙 Volver al menú principal")
        
        choice = input("\nSelecciona una opción (1-3): ").strip()
        
        if choice == "1":
            self.start_server()
        elif choice == "2":
            if self.configure_ngrok_menu():
                self.start_server()
        # Opción 3 o cualquier otra cosa regresa al menú principal
    
    def start_existing_server(self):
        """Inicia un servidor existente"""
        if not os.path.exists(self.server_dir):
            print("❌ No hay ningún servidor creado")
            input("Presiona Enter para continuar...")
            return
        
        self.start_server()
    
    def start_server(self):
        """Inicia el servidor de Minecraft"""
        if not os.path.exists(self.server_dir):
            print("❌ No hay ningún servidor creado")
            input("Presiona Enter para continuar...")
            return
        
        original_dir = os.getcwd()
        os.chdir(self.server_dir)
        
        if not os.path.exists("start_server.sh"):
            print("❌ No se encontró el script de inicio")
            os.chdir(original_dir)
            input("Presiona Enter para continuar...")
            return
        
        print("🚀 Iniciando servidor de Minecraft...")
        print("⚠️  Para detener el servidor, escribe 'stop' en la consola del servidor")
        print("🌐 Si configuraste ngrok, verifica la URL en http://localhost:4040")
        print()
        
        # Crear mensaje de información
        info_msg = """
        ═══════════════════════════════════════════════════════════
        🎮 SERVIDOR MINECRAFT INICIANDO...
        
        📋 INFORMACIÓN IMPORTANTE:
        • Para detener el servidor: escribe 'stop' en la consola
        • Panel de ngrok: http://localhost:4040
        • Los archivos de IP se generarán automáticamente si usas ngrok
        
        📁 ARCHIVOS DE IP GENERADOS:
        • server_ip.txt - Información completa del servidor
        • ip.txt - Solo la dirección IP
        • server_info.json - Información en formato JSON
        
        ⏰ Esperando conexión de ngrok...
        ═══════════════════════════════════════════════════════════
        """
        print(info_msg)
        
        try:
            # Iniciar ngrok si está configurado
            ngrok_started = False
            if os.path.exists("ngrok") and os.path.exists("ngrok.yml"):
                ngrok_started = self.start_ngrok()
            
            # Esperar un poco más si ngrok se inició para asegurar que obtenga la IP
            if ngrok_started:
                print("⏰ Dando tiempo adicional para obtener la IP de ngrok...")
                time.sleep(5)
                # Intentar obtener la IP una vez más
                self.get_and_save_ngrok_ip()
            
            print("\n" + "="*60)
            print("🚀 INICIANDO SERVIDOR MINECRAFT...")
            print("="*60)
            
            # Iniciar servidor
            subprocess.run(['./start_server.sh'])
            
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
        except Exception as e:
            print(f"❌ Error ejecutando el servidor: {e}")
        finally:
            os.chdir(original_dir)
            print("\n" + "="*60)
            print("📊 INFORMACIÓN POST-EJECUCIÓN")
            print("="*60)
            
            # Mostrar información de archivos creados
            ip_files = ["server_ip.txt", "ip.txt", "server_info.json"]
            for ip_file in ip_files:
                full_path = os.path.join(self.server_dir, ip_file)
                if os.path.exists(full_path):
                    print(f"✅ {ip_file} - Creado correctamente")
                else:
                    print(f"❌ {ip_file} - No se pudo crear")
            
            print(f"\n📁 Archivos ubicados en: {os.path.abspath(self.server_dir)}")
            input("\nPresiona Enter para continuar...")
    
    def manage_server_menu(self):
        """Menú de gestión del servidor"""
        if not os.path.exists(self.server_dir):
            print("❌ No hay ningún servidor creado")
            input("Presiona Enter para continuar...")
            return
        
        while True:
            self.print_header()
            print("⚙️  GESTIONAR SERVIDOR")
            print("-" * 30)
            
            # Mostrar información del servidor
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                print(f"📊 Servidor actual: {config['server_type'].title()} {config['version']}")
                print(f"📅 Creado: {config['created_at']}")
            else:
                print("📊 Información del servidor no disponible")
            
            # Mostrar IP del servidor si existe
            ip_file = os.path.join(self.server_dir, "server_ip.txt")
            if os.path.exists(ip_file):
                try:
                    with open(ip_file, 'r') as f:
                        content = f.read()
                        # Extraer solo la IP de la línea que contiene "📍 IP del Servidor:"
                        for line in content.split('\n'):
                            if "📍 IP del Servidor:" in line:
                                ip = line.split(': ')[1]
                                print(f"🌐 IP actual: {ip}")
                                break
                except:
                    pass
            
            print()
            print("1. 📝 Editar server.properties")
            print("2. 👥 Gestionar operadores")
            print("3. 🌐 Crear/Actualizar archivo de IP")
            print("4. 📊 Ver logs del servidor")
            print("5. 🗑️  Eliminar servidor")
            print("6. 🔙 Volver al menú principal")
            print()
            
            choice = input("Selecciona una opción (1-6): ").strip()
            
            if choice == "1":
                self.edit_server_properties()
            elif choice == "2":
                self.manage_operators()
            elif choice == "3":
                original_dir = os.getcwd()
                os.chdir(self.server_dir)
                self.create_ip_file_manually()
                os.chdir(original_dir)
            elif choice == "4":
                self.view_server_logs()
            elif choice == "5":
                if self.delete_server():
                    break
            elif choice == "6":
                break
            else:
                print("❌ Opción inválida")
                input("Presiona Enter para continuar...")
    
    def edit_server_properties(self):
        """Permite editar el archivo server.properties"""
        properties_file = os.path.join(self.server_dir, "server.properties")
        
        if not os.path.exists(properties_file):
            print("❌ No se encontró el archivo server.properties")
            input("Presiona Enter para continuar...")
            return
        
        print("📝 Editar server.properties")
        print("💡 Se abrirá el archivo en el editor nano")
        input("Presiona Enter para continuar...")
        
        try:
            subprocess.run(['nano', properties_file])
            print("✅ Archivo guardado")
        except Exception as e:
            print(f"❌ Error editando el archivo: {e}")
        
        input("Presiona Enter para continuar...")
    
    def manage_operators(self):
        """Gestiona los operadores del servidor"""
        ops_file = os.path.join(self.server_dir, "ops.json")
        
        print("👥 Gestionar Operadores")
        print("-" * 20)
        
        # Mostrar operadores actuales
        if os.path.exists(ops_file):
            try:
                with open(ops_file, 'r') as f:
                    ops = json.load(f)
                
                if ops:
                    print("Operadores actuales:")
                    for i, op in enumerate(ops, 1):
                        print(f"{i}. {op['name']}")
                else:
                    print("No hay operadores configurados")
            except:
                print("Error leyendo el archivo de operadores")
        else:
            print("No hay operadores configurados")
        
        print()
        username = input("Ingresa el nombre de usuario para hacer operador (o Enter para cancelar): ").strip()
        
        if username:
            # Nota: En un servidor real, necesitarías el UUID del jugador
            print(f"💡 Para hacer operador a '{username}', ejecuta este comando en la consola del servidor:")
            print(f"   op {username}")
        
        input("Presiona Enter para continuar...")
    
    def delete_server(self):
        """Elimina el servidor actual"""
        print("🗑️  ELIMINAR SERVIDOR")
        print("⚠️  Esta acción no se puede deshacer")
        print()
        
        confirm = input("¿Estás seguro de que quieres eliminar el servidor? (escriba 'ELIMINAR'): ").strip()
        
        if confirm == "ELIMINAR":
            try:
                if os.path.exists(self.server_dir):
                    shutil.rmtree(self.server_dir)
                
                if os.path.exists(self.config_file):
                    os.remove(self.config_file)
                
                print("✅ Servidor eliminado correctamente")
                input("Presiona Enter para continuar...")
                return True
                
            except Exception as e:
                print(f"❌ Error eliminando el servidor: {e}")
                input("Presiona Enter para continuar...")
        else:
            print("❌ Eliminación cancelada")
            input("Presiona Enter para continuar...")
        
        return False
    
    def view_server_logs(self):
        """Muestra los logs del servidor"""
        logs_dir = os.path.join(self.server_dir, "logs")
        latest_log = os.path.join(logs_dir, "latest.log")
        
        if not os.path.exists(latest_log):
            print("❌ No se encontraron logs del servidor")
            input("Presiona Enter para continuar...")
            return
        
        print("📊 Logs del servidor (últimas 50 líneas)")
        print("-" * 40)
        
        try:
            subprocess.run(['tail', '-n', '50', latest_log])
        except Exception as e:
            print(f"❌ Error mostrando los logs: {e}")
        
        input("\nPresiona Enter para continuar...")
    
    def configure_ngrok_menu(self):
        """Menú de configuración de ngrok"""
        self.print_header()
        print("🌐 CONFIGURAR NGROK")
        print("-" * 30)
        print("ngrok permite que otros jugadores se conecten a tu servidor")
        print("desde internet, incluso si estás detrás de un firewall.")
        print()
        
        print("📍 Regiones disponibles:")
        regions = list(self.ngrok_regions.keys())
        for i, region in enumerate(regions, 1):
            print(f"{i}. {region} - {self.ngrok_regions[region]}")
        print()
        
        while True:
            try:
                region_choice = int(input(f"Selecciona una región (1-{len(regions)}): "))
                if 1 <= region_choice <= len(regions):
                    selected_region = regions[region_choice - 1]
                    break
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Por favor ingresa un número")
        
        print(f"\n🌐 Configurando ngrok en región: {self.ngrok_regions[selected_region]}")
        
        # Cambiar al directorio del servidor o crearlo si no existe
        if not os.path.exists(self.server_dir):
            os.makedirs(self.server_dir)
        
        original_dir = os.getcwd()
        os.chdir(self.server_dir)
        
        success = self.setup_ngrok(selected_region)
        
        os.chdir(original_dir)
        
        if success:
            print("✅ ngrok configurado correctamente")
            print("💡 El túnel se iniciará automáticamente cuando ejecutes el servidor")
        else:
            print("❌ Error configurando ngrok")
        
        input("Presiona Enter para continuar...")
        return success

def main():
    """Función principal"""
    try:
        manager = MinecraftServerManager()
        manager.show_main_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        print("Por favor reporta este error si persiste")

if __name__ == "__main__":
    main()
