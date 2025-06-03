# fix_setup.py - Script de reparación rápida para problemas de setup

import os

def create_missing_files():
    """Crea los archivos que faltaron en el setup"""
    
    print("🔧 REPARANDO CONFIGURACIÓN...")
    
    # Contenido de los README sin caracteres especiales
    readme_contents = {
        "data/README.md": """# Data Directory

Coloca aqui tus archivos CSV de datos historicos:

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

Los resultados del backtesting se guardan automaticamente aqui:

## Archivos generados:
- `cfd_backtest_[INSTRUMENT]_[TIMESTAMP].csv` - Trades detallados
- `equity_curve_[INSTRUMENT]_[TIMESTAMP].png` - Grafica de equity
- `optimization_[INSTRUMENT]_[TIMESTAMP].csv` - Resultados de optimizacion
- `best_config_[INSTRUMENT]_[TIMESTAMP].txt` - Mejor configuracion encontrada
""",
        
        "logs/README.md": """# Logs Directory

Logs del sistema y debugging:

- `backtest.log` - Log principal del backtesting
- `errors.log` - Log de errores
- `debug.log` - Log de debugging (si esta activado)
"""
    }
    
    # Crear archivos con codificación UTF-8
    for file_path, content in readme_contents.items():
        try:
            # Crear directorio si no existe
            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                print(f"✅ Directorio creado: {directory}")
            
            # Crear archivo
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Archivo creado: {file_path}")
            else:
                print(f"📄 Archivo ya existe: {file_path}")
                
        except Exception as e:
            print(f"❌ Error creando {file_path}: {e}")
    
    # Crear archivos .gitkeep
    gitkeep_dirs = ["results", "logs"]
    for directory in gitkeep_dirs:
        gitkeep_path = f"{directory}/.gitkeep"
        try:
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w', encoding='utf-8') as f:
                    f.write("")
                print(f"✅ Archivo .gitkeep creado: {gitkeep_path}")
            else:
                print(f"📄 .gitkeep ya existe: {gitkeep_path}")
        except Exception as e:
            print(f"❌ Error creando .gitkeep en {directory}: {e}")

def show_next_steps():
    """Muestra los próximos pasos"""
    print(f"\n🎉 ¡REPARACIÓN COMPLETADA!")
    print("=" * 50)
    
    print(f"\n📋 PRÓXIMOS PASOS:")
    print(f"1️⃣  Activar el entorno virtual:")
    print(f"    venv\\Scripts\\activate")
    
    print(f"\n2️⃣  Instalar dependencias:")
    print(f"    pip install -r requirements.txt")
    
    print(f"\n3️⃣  Verificar instalación:")
    print(f"    python check_dependencies.py")
    
    print(f"\n4️⃣  Configurar y ejecutar:")
    print(f"    python main.py --config")
    print(f"    python main.py")
    
    print("=" * 50)

def main():
    print("=" * 50)
    print("REPARACIÓN RÁPIDA DEL SETUP")
    print("=" * 50)
    
    create_missing_files()
    show_next_steps()

if __name__ == "__main__":
    main()