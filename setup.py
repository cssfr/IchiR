# setup.py - Script de configuración inicial del proyecto

import os
import sys
import subprocess
import platform

def create_directory_if_not_exists(path):
    """Crea un directorio si no existe"""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"✅ Directorio creado: {path}")
    else:
        print(f"📁 Directorio ya existe: {path}")

def create_file_if_not_exists(path, content=""):
    """Crea un archivo si no existe"""
    if not os.path.exists(path):
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Archivo creado: {path}")
    else:
        print(f"📄 Archivo ya existe: {path}")

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Error: Python {version.major}.{version.minor} detectado")
        print("❌ Se requiere Python 3.8 o superior")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
        return True

def setup_virtual_environment():
    """Configura el entorno virtual"""
    venv_path = "venv"
    
    print(f"\n🐍 CONFIGURANDO ENTORNO VIRTUAL...")
    
    if os.path.exists(venv_path):
        print(f"📁 Entorno virtual ya existe en: {venv_path}")
        return True
    
    try:
        # Crear entorno virtual
        print("⏳ Creando entorno virtual...")
        subprocess.run([sys.executable, "-m", "venv", venv_path], check=True)
        print(f"✅ Entorno virtual creado en: {venv_path}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando entorno virtual: {e}")
        return False
    except FileNotFoundError:
        print("❌ Error: El módulo venv no está disponible")
        print("💡 Instala con: sudo apt-get install python3-venv (Ubuntu/Debian)")
        return False

def get_activation_command():
    """Retorna el comando de activación según el OS"""
    system = platform.system().lower()
    
    if system == "windows":
        return "venv\\Scripts\\activate"
    else:  # Linux/macOS
        return "source venv/bin/activate"

def setup_project_structure():
    """Configura la estructura de directorios del proyecto"""
    print(f"\n📁 CONFIGURANDO ESTRUCTURA DEL PROYECTO...")
    
    # Crear directorios necesarios
    directories = [
        "data",
        "results",
        "logs",
        "docs",
        "tests"
    ]
    
    for directory in directories:
        create_directory_if_not_exists(directory)
    
    # Crear archivos README en directorios importantes
    readme_contents = {
        "data/README.md": """# Data Directory

Coloca aquí tus archivos CSV de datos históricos:

## Estructura requerida:
```
data/
├── UK100_15M.csv      # Datos de 15 minutos para UK100
├── UK100_4H.csv       # Datos de 4 horas para UK100
├── WallStreet30_15M.csv
├── WallStreet30_4H.csv
└── ...
```

## Formato CSV requerido:
```csv
Local time,Open,High,Low,Close,Volume
01.01.2022 00:00:00.000 GMT+0,7850.5,7855.0,7848.0,7852.5,1250
```

O alternativamente:
```csv
timestamp,open,high,low,close,volume
```
""",
        
        "results/README.md": """# Results Directory

Los resultados del backtesting se guardan automáticamente aquí:

## Archivos generados:
- `cfd_backtest_[INSTRUMENT]_[TIMESTAMP].csv` - Trades detallados
- `equity_curve_[INSTRUMENT]_[TIMESTAMP].png` - Gráfica de equity
- `optimization_[INSTRUMENT]_[TIMESTAMP].csv` - Resultados de optimización
- `best_config_[INSTRUMENT]_[TIMESTAMP].txt` - Mejor configuración encontrada
""",
        
        "logs/README.md": """# Logs Directory

Logs del sistema y debugging:

- `backtest.log` - Log principal del backtesting
- `errors.log` - Log de errores
- `debug.log` - Log de debugging (si está activado)
"""
    }
    
    for file_path, content in readme_contents.items():
        create_file_if_not_exists(file_path, content)
    
    # Crear archivo .gitkeep para directorios vacíos
    gitkeep_dirs = ["results", "logs"]
    for directory in gitkeep_dirs:
        create_file_if_not_exists(f"{directory}/.gitkeep", "")

def show_next_steps():
    """Muestra los próximos pasos para el usuario"""
    activation_cmd = get_activation_command()
    
    print(f"\n🎉 ¡CONFIGURACIÓN INICIAL COMPLETADA!")
    print("=" * 60)
    
    print(f"\n📋 PRÓXIMOS PASOS:")
    print(f"1️⃣  Activar el entorno virtual:")
    print(f"    {activation_cmd}")
    
    print(f"\n2️⃣  Instalar dependencias:")
    print(f"    pip install -r requirements.txt")
    
    print(f"\n3️⃣  Verificar instalación:")
    print(f"    python check_dependencies.py")
    
    print(f"\n4️⃣  Configurar el sistema:")
    print(f"    python main.py --config")
    print(f"    # Editar config.py según tus necesidades")
    
    print(f"\n5️⃣  Agregar datos históricos:")
    print(f"    # Colocar archivos CSV en la carpeta data/")
    print(f"    # Ver data/README.md para formato requerido")
    
    print(f"\n6️⃣  Ejecutar backtest:")
    print(f"    python main.py")
    
    print(f"\n💡 COMANDOS ÚTILES:")
    print(f"    python main.py --help           # Ver ayuda")
    print(f"    python optimize.py              # Optimizar parámetros")
    print(f"    deactivate                      # Desactivar venv")
    
    print(f"\n📁 ESTRUCTURA DEL PROYECTO:")
    print(f"    ├── config.py                   # ⚙️  Configuración principal")
    print(f"    ├── main.py                     # ▶️  Script principal")
    print(f"    ├── cfd_backtest_engine.py      # 🔧 Motor de backtesting")
    print(f"    ├── optimize.py                 # 🎯 Optimización")
    print(f"    ├── data/                       # 📊 Datos históricos")
    print(f"    ├── results/                    # 📈 Resultados")
    print(f"    └── venv/                       # 🐍 Entorno virtual")
    
    print("=" * 60)

def main():
    """Función principal del setup"""
    print("=" * 60)
    print("CFD BACKTESTING SYSTEM - CONFIGURACIÓN INICIAL")
    print("=" * 60)
    
    # 1. Verificar Python
    print("🔍 VERIFICANDO PRERREQUISITOS...")
    if not check_python_version():
        sys.exit(1)
    
    # 2. Configurar entorno virtual
    if not setup_virtual_environment():
        print("\n❌ No se pudo configurar el entorno virtual")
        print("💡 Puedes continuar sin entorno virtual, pero no es recomendado")
        
        continue_anyway = input("\n¿Continuar sin entorno virtual? (y/N): ").lower().strip()
        if continue_anyway != 'y':
            sys.exit(1)
    
    # 3. Configurar estructura del proyecto
    setup_project_structure()
    
    # 4. Mostrar próximos pasos
    show_next_steps()

if __name__ == "__main__":
    main()