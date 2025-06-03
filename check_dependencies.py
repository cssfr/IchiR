# check_dependencies.py - Verificador de dependencias del sistema

import sys
import subprocess

def check_python_version():
    """Verifica la versión de Python"""
    version = sys.version_info
    print(f"🐍 Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        return False
    else:
        print("✅ Versión de Python compatible")
        return True

def check_package(package_name, import_name=None):
    """Verifica si un paquete está instalado"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - NO INSTALADO")
        return False

def get_package_version(package_name):
    """Obtiene la versión de un paquete"""
    try:
        result = subprocess.run([sys.executable, "-c", f"import {package_name}; print({package_name}.__version__)"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "unknown"
    except:
        return "unknown"

def main():
    """Función principal"""
    print("="*60)
    print("CFD BACKTESTING SYSTEM - VERIFICACIÓN DE DEPENDENCIAS")
    print("="*60)
    
    # Verificar Python
    print("\n🔍 VERIFICANDO PYTHON:")
    python_ok = check_python_version()
    
    # Lista de dependencias requeridas
    required_packages = [
        ("pandas", "pandas"),
        ("numpy", "numpy"), 
        ("ta", "ta"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn")
    ]
    
    # Verificar paquetes
    print("\n🔍 VERIFICANDO DEPENDENCIAS:")
    all_installed = True
    
    for package_name, import_name in required_packages:
        is_installed = check_package(package_name, import_name)
        if not is_installed:
            all_installed = False
    
    # Mostrar versiones de paquetes clave
    print("\n📋 VERSIONES INSTALADAS:")
    for package_name, import_name in required_packages:
        try:
            version = get_package_version(import_name)
            print(f"   {package_name}: {version}")
        except:
            print(f"   {package_name}: no disponible")
    
    # Resultado final
    print("\n" + "="*60)
    if python_ok and all_installed:
        print("🎉 ¡SISTEMA LISTO!")
        print("✅ Todas las dependencias están instaladas correctamente")
        print("✅ Puedes ejecutar el backtesting sin problemas")
        
        print("\n🚀 PRÓXIMOS PASOS:")
        print("1. Configura tu instrumento en config.py")
        print("2. Coloca tus archivos CSV en la carpeta data/")
        print("3. Ejecuta: python main.py")
        
    else:
        print("❌ SISTEMA NO LISTO")
        if not python_ok:
            print("❌ Actualiza Python a versión 3.8 o superior")
        if not all_installed:
            print("❌ Instala las dependencias faltantes con:")
            print("   pip install -r requirements.txt")
    
    print("="*60)

if __name__ == "__main__":
    main()