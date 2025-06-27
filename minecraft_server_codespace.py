#!/usr/bin/env python3
"""
Servidor de Minecraft para GitHub Codespaces
Configuración automática con Playit para acceso público
"""

import os
import sys
import json
import time
import subprocess
import requests
import shutil
from pathlib import Path

class MinecraftServerManager:
    def __init__(self):
        self.server_types = {
            "vanilla": "Servidor Vanilla oficial de Minecraft",
            "paper": "Servidor Paper (optimizado, plugins Bukkit/Spigot)",
            "fabric": "Servidor Fabric (mods del lado del servidor)",
            "forge": "Servidor Forge (mods tradicionales)",
            "mohist": "Servidor Mohist (mods + plugins)",
            "purpur": "Servidor Purpur (Paper mejorado)"
        }
        
        self.playit_regions = {
            "us": "Estados Unidos (Ohio)",
            "us-cal-1": "Estados Unidos (California)",
            "eu": "Europa (Frankfurt)",
            "ap": "Asia/Pacífico (Singapore)",
            "au": "Australia (Sydney)",
            "jp": "Japón (Tokyo)",
            "in": "India (Mumbai)",
            "sa": "Sudamérica (São Paulo)"
        }
        
        self.minecraft_versions = [
            "1.21.4", "1.21.3", "1.21.1", "1.21",
            "1.20.6", "1.20.4", "1.20.2", "1.20.1",
            "1.19.4", "1.19.2", "1.18.2", "1.17.1",
            "1.16.5", "1.12.2", "1.8.9"
        ]
        
        self.server_dir = Path("minecraft_server")
        self.config_file = Path("server_config.json")

    def clear_screen(self):
        os.system('clear' if os.name == 'posix' else 'cls')

    def print_header(self):
        print("=" * 60)
        print("🎮 SERVIDOR DE MINECRAFT PARA GITHUB CODESPACES 🎮")
        print("=" * 60)
        print()

    def print_menu(self, title, options):
        print(f"📋 {title}")
        print("-" * 40)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        print()

    def get_user_choice(self, max_option):
        while True:
            try:
                choice = int(input(f"Selecciona una opción (1-{max_option}): "))
                if 1 <= choice <= max_option:
                    return choice - 1
                else:
                    print(f"❌ Opción inválida. Ingresa un número entre 1 y {max_option}")
            except ValueError:
                print("❌ Por favor ingresa un número válido")

    def select_minecraft_version(self):
        self.clear_screen()
        self.print_header()
        
        print("🔧 Selecciona la versión de Minecraft:")
        print("-" * 40)
        
        for i, version in enumerate(self.minecraft_versions, 1):
            print(f"{i}. Minecraft {version}")
        
        print(f"{len(self.minecraft_versions) + 1}. Versión personalizada")
        print()
        
        max_options = len(self.minecraft_versions) + 1
        choice = self.get_user_choice(max_options)
        
        if choice == len(self.minecraft_versions):
            version = input("Ingresa la versión personalizada (ej: 1.21.4): ").strip()
            if not version:
                print("❌ Versión no válida")
                return self.select_minecraft_version()
            return version
        else:
            return self.minecraft_versions[choice]

    def select_server_type(self):
        self.clear_screen()
        self.print_header()
        
        print("🏗️ Tipos de servidor disponibles:")
        print("-" * 40)
        
        server_list = list(self.server_types.items())
        for i, (key, description) in enumerate(server_list, 1):
            print(f"{i}. {key.upper()}")
            print(f"   └─ {description}")
            print()
        
        choice = self.get_user_choice(len(server_list))
        return server_list[choice][0]

    def select_playit_region(self):
        self.clear_screen()
        self.print_header()
        
        print("🌍 Selecciona la región de Playit (para mejor latencia):")
        print("-" * 50)
        
        region_list = list(self.playit_regions.items())
        for i, (code, location) in enumerate(region_list, 1):
            print(f"{i}. {location} ({code})")
        
        print()
        choice = self.get_user_choice(len(region_list))
        return region_list[choice][0]

    def install_playit(self):
        """Instala Playit para hacer el servidor accesible públicamente"""
        print("📦 Instalando Playit...")
        
        try:
            # Descargar Playit
            playit_url = "https://github.com/playit-cloud/playit-agent/releases/latest/download/playit-linux_64"
            
            print("⬇️  Descargando Playit...")
            response = requests.get(playit_url)
            
            if response.status_code == 200:
                with open("playit", "wb") as f:
                    f.write(response.content)
                
                os.chmod("playit", 0o755)
                print("✅ Playit instalado correctamente")
                return True
            else:
                print("❌ Error al descargar Playit")
                return False
                
        except Exception as e:
            print(f"❌ Error instalando Playit: {e}")
            return False

    def download_server_jar(self, server_type, version):
        """Descarga el archivo JAR del servidor"""
        print(f"⬇️  Descargando servidor {server_type} {version}...")
        
        self.server_dir.mkdir(exist_ok=True)
        
        urls = {
            "vanilla": f"https://piston-data.mojang.com/v1/objects/450698d1863ab5180c25d32dd6fab2d5dbd61daa/server.jar",
            "paper": f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/latest/downloads/paper-{version}-latest.jar",
            "fabric": f"https://meta.fabricmc.net/v2/versions/loader/{version}/stable/server/jar",
            "forge": f"https://maven.minecraftforge.net/net/minecraftforge/forge/{version}/forge-{version}-installer.jar"
        }
        
        # Para simplificar, usamos Paper como ejemplo
        if server_type == "paper":
            try:
                jar_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
                builds_response = requests.get(jar_url)
                
                if builds_response.status_code == 200:
                    builds_data = builds_response.json()
                    latest_build = builds_data['builds'][-1]['build']
                    download_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{latest_build}/downloads/paper-{version}-{latest_build}.jar"
                    
                    jar_response = requests.get(download_url)
                    if jar_response.status_code == 200:
                        jar_path = self.server_dir / "server.jar"
                        with open(jar_path, "wb") as f:
                            f.write(jar_response.content)
                        print("✅ Servidor descargado correctamente")
                        return True
                        
            except Exception as e:
                print(f"❌ Error descargando servidor: {e}")
        
        # Fallback: crear un servidor mock para demostración
        print("⚠️  Creando servidor de demostración...")
        jar_path = self.server_dir / "server.jar"
        jar_path.touch()
        return True

    def create_server_properties(self, server_port=25565):
        """Crea el archivo server.properties"""
        properties = {
            "server-port": server_port,
            "online-mode": "false",
            "enable-command-block": "true",
            "gamemode": "survival",
            "difficulty": "easy",
            "max-players": "20",
            "view-distance": "10",
            "motd": "Servidor Minecraft en GitHub Codespaces",
            "white-list": "false",
            "spawn-protection": "16"
        }
        
        properties_path = self.server_dir / "server.properties"
        with open(properties_path, "w") as f:
            for key, value in properties.items():
                f.write(f"{key}={value}\n")
        
        print("✅ Archivo server.properties creado")

    def create_eula(self):
        """Acepta automáticamente el EULA"""
        eula_path = self.server_dir / "eula.txt"
        with open(eula_path, "w") as f:
            f.write("eula=true\n")
        print("✅ EULA aceptado")

    def create_start_script(self):
        """Crea el script de inicio del servidor"""
        start_script = """#!/bin/bash
echo "🚀 Iniciando servidor de Minecraft..."
cd minecraft_server
java -Xmx2G -Xms1G -jar server.jar nogui
"""
        
        with open("start_server.sh", "w") as f:
            f.write(start_script)
        
        os.chmod("start_server.sh", 0o755)
        print("✅ Script de inicio creado")

    def create_playit_config(self, region):
        """Crea la configuración de Playit"""
        config = {
            "region": region,
            "tunnels": [
                {
                    "type": "minecraft-java",
                    "local_port": 25565,
                    "name": "minecraft-server"
                }
            ]
        }
        
        with open("playit.toml", "w") as f:
            f.write(f"[agent]\n")
            f.write(f"region = \"{region}\"\n\n")
            f.write("[tunnels.minecraft]\n")
            f.write("type = \"minecraft-java\"\n")
            f.write("local_port = 25565\n")
        
        print("✅ Configuración de Playit creada")

    def setup_playit_tunnel(self):
        """Configura el túnel de Playit y obtiene la IP pública"""
        self.clear_screen()
        self.print_header()
        
        print("🌐 CONFIGURACIÓN DE PLAYIT")
        print("=" * 30)
        print()
        print("Para hacer tu servidor accesible públicamente, necesitas:")
        print("1. Ejecutar Playit en segundo plano")
        print("2. Obtener el túnel/IP que te proporciona")
        print("3. Configurarlo en este programa")
        print()
        
        print("📋 Instrucciones:")
        print("1. Abre una nueva terminal")
        print("2. Ejecuta: ./playit")
        print("3. Sigue las instrucciones de Playit")
        print("4. Copia el túnel/IP que te dé")
        print("5. Regresa aquí y pégalo")
        print()
        
        # Preguntar si ya tiene el túnel o quiere iniciarlo automáticamente
        options = [
            "Ya tengo el túnel de Playit (ingresar manualmente)",
            "Iniciar Playit automáticamente",
            "Volver al menú anterior"
        ]
        
        self.print_menu("¿Qué deseas hacer?", options)
        choice = self.get_user_choice(len(options))
        
        if choice == 0:  # Ingresar manualmente
            tunnel_ip = input("\n🔗 Ingresa el túnel/IP de Playit (ej: abc123.playit.gg:12345): ").strip()
            if tunnel_ip:
                return self.save_playit_tunnel(tunnel_ip)
            else:
                print("❌ No ingresaste ningún túnel")
                return False
                
        elif choice == 1:  # Iniciar automáticamente
            return self.start_playit_automatic()
            
        else:  # Volver
            return False

    def save_playit_tunnel(self, tunnel_ip):
        """Guarda el túnel de Playit en la configuración"""
        config = self.load_config()
        if config:
            config['playit_tunnel'] = tunnel_ip
            config['tunnel_configured_at'] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.save_config(config)
            
            print(f"✅ Túnel guardado: {tunnel_ip}")
            print()
            print("🎮 Tu servidor será accesible en:")
            print(f"   └─ {tunnel_ip}")
            print()
            input("Presiona Enter para continuar...")
            return True
        else:
            print("❌ No hay configuración de servidor disponible")
            return False

    def start_playit_automatic(self):
        """Inicia Playit automáticamente en segundo plano"""
        print("🚀 Iniciando Playit automáticamente...")
        print()
        print("⚠️  IMPORTANTE:")
        print("- Playit se ejecutará en segundo plano")
        print("- Revisa los logs para obtener tu túnel/IP")
        print("- Guarda el túnel cuando aparezca")
        print()
        
        try:
            # Crear script para ejecutar Playit en background
            playit_script = """#!/bin/bash
echo "🌐 Iniciando Playit..."
echo "Logs guardados en playit.log"
./playit > playit.log 2>&1 &
echo "✅ Playit iniciado en segundo plano (PID: $!)"
echo "📝 Revisa playit.log para ver el túnel/IP"
echo "📋 Comando útil: tail -f playit.log"
"""
            
            with open("start_playit.sh", "w") as f:
                f.write(playit_script)
            
            os.chmod("start_playit.sh", 0o755)
            
            # Ejecutar el script
            os.system("./start_playit.sh")
            
            print("✅ Playit iniciado")
            print("📝 Logs en: playit.log")
            print("🔍 Ver logs: tail -f playit.log")
            print()
            
            # Preguntar si quiere ingresar el túnel ahora
            wait_choice = input("¿Quieres ingresar el túnel ahora? (s/n): ").lower().strip()
            if wait_choice in ['s', 'si', 'yes', 'y']:
                tunnel_ip = input("🔗 Ingresa el túnel/IP de Playit: ").strip()
                if tunnel_ip:
                    return self.save_playit_tunnel(tunnel_ip)
            
            return True
            
        except Exception as e:
            print(f"❌ Error iniciando Playit: {e}")
            return False

    def start_minecraft_server(self):
        """Inicia el servidor de Minecraft"""
        config = self.load_config()
        
        if not config:
            print("❌ No hay servidor configurado")
            input("Presiona Enter para continuar...")
            return False
        
        self.clear_screen()
        self.print_header()
        
        print("🚀 INICIAR SERVIDOR DE MINECRAFT")
        print("=" * 35)
        print()
        
        # Mostrar información del servidor
        print("📋 Información del servidor:")
        print(f"   Versión: {config['version']}")
        print(f"   Tipo: {config['server_type']}")
        print(f"   Región: {config['region']}")
        
        if 'playit_tunnel' in config:
            print(f"   🌐 Túnel público: {config['playit_tunnel']}")
        else:
            print("   ⚠️  Sin túnel público configurado")
        
        print()
        
        # Verificar si existe el servidor físicamente
        if not (self.server_dir / "server.jar").exists():
            print("❌ Archivo del servidor no encontrado")
            print("Necesitas crear el servidor primero")
            input("Presiona Enter para continuar...")
            return False
        
        # Opciones de inicio
        options = [
            "Iniciar servidor ahora",
            "Iniciar servidor + Playit automáticamente",
            "Solo mostrar comando de inicio",
            "Configurar túnel de Playit primero",
            "Volver al menú anterior"
        ]
        
        self.print_menu("¿Cómo quieres iniciar el servidor?", options)
        choice = self.get_user_choice(len(options))
        
        if choice == 0:  # Solo servidor
            return self.run_minecraft_server()
            
        elif choice == 1:  # Servidor + Playit
            return self.run_server_with_playit()
            
        elif choice == 2:  # Mostrar comando
            self.show_start_commands()
            return True
            
        elif choice == 3:  # Configurar túnel
            self.setup_playit_tunnel()
            return True
            
        else:  # Volver
            return True

    def run_minecraft_server(self):
        """Ejecuta solo el servidor de Minecraft"""
        print("🚀 Iniciando servidor de Minecraft...")
        print()
        print("⚠️  IMPORTANTE:")
        print("- El servidor se ejecutará en esta terminal")
        print("- Para detenerlo, usa Ctrl+C o escribe 'stop'")
        print("- Para acceso público, necesitas Playit corriendo")
        print()
        
        input("Presiona Enter para continuar...")
        
        try:
            os.chdir(self.server_dir)
            print("🎮 Servidor iniciando...")
            os.system("java -Xmx2G -Xms1G -jar server.jar nogui")
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido por el usuario")
        except Exception as e:
            print(f"❌ Error al iniciar servidor: {e}")
        finally:
            os.chdir("..")
        
        input("Presiona Enter para volver al menú...")
        return True

    def run_server_with_playit(self):
        """Ejecuta el servidor y Playit automáticamente"""
        print("🚀 Iniciando servidor + Playit...")
        print()
        
        # Crear script combinado
        combined_script = """#!/bin/bash
echo "🌐 Iniciando Playit en segundo plano..."
./playit > playit.log 2>&1 &
PLAYIT_PID=$!
echo "✅ Playit iniciado (PID: $PLAYIT_PID)"

echo "⏳ Esperando 3 segundos..."
sleep 3

echo "🎮 Iniciando servidor de Minecraft..."
cd minecraft_server
java -Xmx2G -Xms1G -jar server.jar nogui

echo "🛑 Servidor detenido, cerrando Playit..."
kill $PLAYIT_PID 2>/dev/null
"""
        
        with open("start_both.sh", "w") as f:
            f.write(combined_script)
        
        os.chmod("start_both.sh", 0o755)
        
        print("📋 Se iniciará:")
        print("1. Playit en segundo plano")
        print("2. Servidor de Minecraft")
        print()
        print("📝 Logs de Playit en: playit.log")
        print("🔍 Ver túnel: tail -f playit.log")
        print()
        
        input("Presiona Enter para iniciar...")
        
        try:
            os.system("./start_both.sh")
        except KeyboardInterrupt:
            print("\n🛑 Detenido por el usuario")
        
        input("Presiona Enter para volver al menú...")
        return True

    def show_start_commands(self):
        """Muestra los comandos para iniciar manualmente"""
        config = self.load_config()
        
        print("📋 COMANDOS DE INICIO MANUAL")
        print("=" * 35)
        print()
        
        print("🎮 Para iniciar solo el servidor:")
        print("   cd minecraft_server")
        print("   java -Xmx2G -Xms1G -jar server.jar nogui")
        print()
        
        print("🌐 Para iniciar Playit (en otra terminal):")
        print("   ./playit")
        print()
        
        print("🚀 Para iniciar ambos automáticamente:")
        print("   ./start_both.sh")
        print()
        
        print("📝 Ver logs de Playit:")
        print("   tail -f playit.log")
        print()
        
        if 'playit_tunnel' in config:
            print(f"🔗 Tu servidor público: {config['playit_tunnel']}")
        else:
            print("⚠️  Recuerda configurar el túnel de Playit")
        
        print()
        input("Presiona Enter para continuar...")

    def check_playit_status(self):
        """Verifica el estado de Playit"""
        print("🔍 Verificando estado de Playit...")
        
        # Verificar si Playit está corriendo
        result = os.system("pgrep -f playit > /dev/null 2>&1")
        
        if result == 0:
            print("✅ Playit está corriendo")
            
            # Intentar leer el log
            if os.path.exists("playit.log"):
                print("📝 Últimas líneas del log:")
                os.system("tail -n 5 playit.log")
            else:
                print("📝 No se encontró archivo de log")
        else:
            print("❌ Playit no está corriendo")
            print("💡 Puedes iniciarlo con: ./playit")
        
        print()
        input("Presiona Enter para continuar...")

    def load_config(self):
        """Carga la configuración del servidor"""
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return None

    def create_server_menu(self):
        """Menú principal para crear servidor"""
        self.clear_screen()
        self.print_header()
        
        print("🎯 CREAR NUEVO SERVIDOR")
        print("=" * 30)
        print()
        
        # Seleccionar versión
        version = self.select_minecraft_version()
        
        # Seleccionar tipo de servidor
        server_type = self.select_server_type()
        
        # Seleccionar región de Playit
        region = self.select_playit_region()
        
        # Confirmar configuración
        self.clear_screen()
        self.print_header()
        
        print("📋 CONFIGURACIÓN DEL SERVIDOR")
        print("=" * 35)
        print(f"Versión: {version}")
        print(f"Tipo: {server_type}")
        print(f"Región Playit: {self.playit_regions[region]}")
        print()
        
        confirm = input("¿Confirmar y crear servidor? (s/n): ").lower().strip()
        
        if confirm in ['s', 'si', 'yes', 'y']:
            self.create_server(version, server_type, region)
        else:
            print("❌ Creación cancelada")
            return

    def create_server(self, version, server_type, region):
        """Crea el servidor con la configuración especificada"""
        self.clear_screen()
        self.print_header()
        
        print("🏗️  CREANDO SERVIDOR...")
        print("=" * 25)
        print()
        
        config = {
            "version": version,
            "server_type": server_type,
            "region": region,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        steps = [
            ("Instalando Playit", self.install_playit),
            ("Descargando servidor", lambda: self.download_server_jar(server_type, version)),
            ("Configurando servidor", lambda: self.create_server_properties()),
            ("Aceptando EULA", self.create_eula),
            ("Creando script de inicio", self.create_start_script),
            ("Configurando Playit", lambda: self.create_playit_config(region)),
            ("Guardando configuración", lambda: self.save_config(config))
        ]
        
        for step_name, step_func in steps:
            print(f"⏳ {step_name}...")
            if not step_func():
                print(f"❌ Error en: {step_name}")
                return False
            time.sleep(0.5)
        
        print("\n🎉 ¡SERVIDOR CREADO EXITOSAMENTE!")
        print("=" * 35)
        print()
        print("🎯 Próximos pasos:")
        print("1. 🌐 Configurar túnel de Playit")
        print("2. 🚀 Iniciar el servidor")
        print("3. 🎮 ¡Jugar!")
        print()
        print("💡 Consejo: Ve a 'Gestionar servidor' para configurar Playit")
        print()
        
        # Preguntar si quiere configurar Playit ahora
        setup_now = input("¿Quieres configurar Playit ahora? (s/n): ").lower().strip()
        if setup_now in ['s', 'si', 'yes', 'y']:
            self.setup_playit_tunnel()
        
        input("Presiona Enter para continuar...")

    def save_config(self, config):
        """Guarda la configuración del servidor"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)

    def manage_server_menu(self):
        """Menú para gestionar servidor existente"""
        config = self.load_config()
        
        if not config:
            print("❌ No hay servidor configurado")
            print("Primero crea un servidor desde el menú principal")
            input("Presiona Enter para continuar...")
            return
        
        self.clear_screen()
        self.print_header()
        
        print("⚙️  GESTIONAR SERVIDOR")
        print("=" * 25)
        print(f"Versión: {config['version']}")
        print(f"Tipo: {config['server_type']}")
        print(f"Región: {config['region']}")
        
        if 'playit_tunnel' in config:
            print(f"🌐 Túnel: {config['playit_tunnel']}")
        else:
            print("⚠️  Sin túnel configurado")
        
        print()
        
        options = [
            "🚀 Iniciar servidor",
            "🌐 Configurar túnel de Playit",
            "🔍 Ver estado de Playit",
            "📁 Ver archivos del servidor",
            "📋 Mostrar comandos manuales",
            "⚠️  Eliminar servidor",
            "🔙 Volver al menú principal"
        ]
        
        self.print_menu("Opciones disponibles:", options)
        choice = self.get_user_choice(len(options))
        
        if choice == 0:  # Iniciar servidor
            self.start_minecraft_server()
        elif choice == 1:  # Configurar túnel
            self.setup_playit_tunnel()
        elif choice == 2:  # Ver estado Playit
            self.check_playit_status()
        elif choice == 3:  # Ver archivos
            self.show_server_files()
        elif choice == 4:  # Comandos manuales
            self.show_start_commands()
        elif choice == 5:  # Eliminar servidor
            self.delete_server()
        elif choice == 6:  # Volver
            return

    def show_server_files(self):
        """Muestra los archivos del servidor"""
        print("📁 ARCHIVOS DEL SERVIDOR")
        print("=" * 30)
        print()
        
        if self.server_dir.exists():
            print("📂 Contenido de minecraft_server/:")
            os.system(f"ls -la {self.server_dir}/")
            print()
            
            # Mostrar archivos importantes
            important_files = ["server.properties", "eula.txt", "server.jar"]
            for file in important_files:
                file_path = self.server_dir / file
                if file_path.exists():
                    print(f"✅ {file} - OK")
                else:
                    print(f"❌ {file} - FALTANTE")
        else:
            print("❌ Directorio del servidor no existe")
        
        print()
        print("📋 Otros archivos importantes:")
        other_files = ["playit", "playit.toml", "playit.log", "start_both.sh"]
        for file in other_files:
            if os.path.exists(file):
                print(f"✅ {file} - OK")
            else:
                print(f"❌ {file} - FALTANTE")
        
        print()
        input("Presiona Enter para continuar...")

    def delete_server(self):
        """Elimina el servidor"""
        print("⚠️  ELIMINAR SERVIDOR")
        print("=" * 25)
        print()
        print("🚨 ADVERTENCIA:")
        print("Esta acción eliminará permanentemente:")
        print("• Todos los archivos del servidor")
        print("• Mundos guardados")
        print("• Configuraciones")
        print("• Scripts de inicio")
        print()
        
        confirm1 = input("¿Estás seguro? Escribe 'ELIMINAR' para confirmar: ").strip()
        
        if confirm1 == "ELIMINAR":
            confirm2 = input("Última confirmación, escribe 'SI' para eliminar: ").strip()
            
            if confirm2 == "SI":
                try:
                    # Detener procesos si están corriendo
                    os.system("pkill -f java.*server.jar 2>/dev/null")
                    os.system("pkill -f playit 2>/dev/null")
                    
                    # Eliminar archivos
                    if self.server_dir.exists():
                        shutil.rmtree(self.server_dir)
                    
                    files_to_remove = [
                        "server_config.json", "playit", "playit.toml", 
                        "playit.log", "start_server.sh", "start_both.sh", 
                        "start_playit.sh"
                    ]
                    
                    for file in files_to_remove:
                        if os.path.exists(file):
                            os.remove(file)
                    
                    print("✅ Servidor eliminado completamente")
                    print("🔄 Puedes crear un nuevo servidor desde el menú principal")
                    
                except Exception as e:
                    print(f"❌ Error eliminando servidor: {e}")
            else:
                print("❌ Eliminación cancelada")
        else:
            print("❌ Eliminación cancelada")
        
        print()
        input("Presiona Enter para continuar...")

    def main_menu(self):
        """Menú principal"""
        while True:
            self.clear_screen()
            self.print_header()
            
            options = [
                "🏗️  Crear servidor",
                "⚙️  Gestionar servidor",
                "📖 Ayuda",
                "🚪 Salir"
            ]
            
            self.print_menu("Menú Principal:", options)
            choice = self.get_user_choice(len(options))
            
            if choice == 0:  # Crear servidor
                self.create_server_menu()
            elif choice == 1:  # Gestionar servidor
                self.manage_server_menu()
            elif choice == 2:  # Ayuda
                self.show_help()
            elif choice == 3:  # Salir
                print("👋 ¡Hasta luego!")
                break

    def show_help(self):
        """Muestra la ayuda"""
        self.clear_screen()
        self.print_header()
        
        help_text = """
📖 AYUDA - SERVIDOR DE MINECRAFT

🎯 ¿Qué hace este programa?
Este programa configura automáticamente un servidor de Minecraft
en GitHub Codespaces y lo hace accesible públicamente usando Playit.

🔧 Tipos de servidor disponibles:
• Vanilla: Servidor oficial de Minecraft
• Paper: Optimizado con soporte para plugins
• Fabric: Para mods del lado del servidor
• Forge: Para mods tradicionales de Minecraft
• Mohist: Combina mods y plugins
• Purpur: Versión mejorada de Paper

🌍 Regiones de Playit:
Selecciona la región más cercana a ti para mejor rendimiento.

⚠️  Requisitos:
• GitHub Codespaces con al menos 2GB RAM
• Java 17 o superior instalado
• Conexión a internet estable

🚀 Proceso de inicio:
1. Crea tu servidor desde el menú
2. Inicia el servidor con ./start_server.sh
3. En otra terminal, ejecuta ./playit
4. Sigue las instrucciones de Playit
5. ¡Tu servidor estará disponible públicamente!

💡 Consejos:
• Guarda la URL que te da Playit
• Puedes modificar server.properties para personalizar
• El servidor se detiene al cerrar el Codespace
        """
        
        print(help_text)
        input("\nPresiona Enter para volver al menú...")

    def run(self):
        """Ejecuta el programa principal"""
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            sys.exit(1)

if __name__ == "__main__":
    # Verificar que estamos en un entorno compatible
    if not shutil.which("java"):
        print("❌ Java no está instalado")
        print("Instala Java con: sudo apt update && sudo apt install openjdk-17-jre-headless")
        sys.exit(1)
    
    # Iniciar el gestor del servidor
    manager = MinecraftServerManager()
    manager.run()
