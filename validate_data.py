# validate_data.py - Validador de archivos CSV para el backtesting

import pandas as pd
import os
from config import DATA_CONFIG, ACTIVE_INSTRUMENT

def detect_csv_format(filepath):
    """Detecta el formato del CSV y muestra información"""
    try:
        # Leer solo las primeras filas para análisis
        df_sample = pd.read_csv(filepath, nrows=5)
        
        print(f"\n📁 Archivo: {filepath}")
        print(f"   Filas totales: {len(pd.read_csv(filepath))}")
        print(f"   Columnas: {list(df_sample.columns)}")
        
        # Detectar columna de tiempo
        time_column = None
        if 'timestamp' in df_sample.columns:
            time_column = 'timestamp'
        elif 'Local time' in df_sample.columns:
            time_column = 'Local time'
        elif 'date' in df_sample.columns:
            time_column = 'date'
        else:
            time_columns = [col for col in df_sample.columns if any(word in col.lower() for word in ['time', 'date'])]
            if time_columns:
                time_column = time_columns[0]
        
        if time_column:
            print(f"   ✅ Columna de tiempo detectada: '{time_column}'")
            print(f"   📅 Muestra de fechas:")
            for i in range(min(3, len(df_sample))):
                print(f"      {df_sample[time_column].iloc[i]}")
        else:
            print(f"   ❌ No se encontró columna de tiempo")
            return False
        
        # Verificar columnas OHLCV
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        available_columns = [col.lower() for col in df_sample.columns]
        
        print(f"   📊 Verificación OHLCV:")
        missing_columns = []
        for col in required_columns:
            if col in available_columns:
                print(f"      ✅ {col}")
            else:
                # Buscar variaciones (Open, OPEN, etc.)
                variations = [c for c in df_sample.columns if c.lower() == col]
                if variations:
                    print(f"      ✅ {col} (como '{variations[0]}')")
                else:
                    print(f"      ❌ {col} - FALTANTE")
                    missing_columns.append(col)
        
        if missing_columns:
            print(f"   ⚠️  Columnas faltantes: {missing_columns}")
            return False
        
        # Mostrar muestra de datos
        print(f"   📋 Muestra de datos:")
        print(df_sample.head(2).to_string(index=False))
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")
        return False

def validate_data_files():
    """Valida los archivos de datos configurados"""
    print("="*60)
    print("VALIDACIÓN DE ARCHIVOS CSV")
    print("="*60)
    print(f"Instrumento activo: {ACTIVE_INSTRUMENT}")
    
    files_to_check = [
        ("15M", DATA_CONFIG["csv_file_path_15m"]),
        ("4H", DATA_CONFIG["csv_file_path_4h"])
    ]
    
    all_valid = True
    
    for timeframe, filepath in files_to_check:
        print(f"\n🔍 VALIDANDO {timeframe}:")
        
        if not os.path.exists(filepath):
            print(f"   ❌ Archivo no encontrado: {filepath}")
            print(f"   💡 Crear archivo o actualizar ruta en config.py")
            all_valid = False
            continue
        
        file_valid = detect_csv_format(filepath)
        if not file_valid:
            all_valid = False
    
    print(f"\n{'='*60}")
    if all_valid:
        print("🎉 ¡TODOS LOS ARCHIVOS SON VÁLIDOS!")
        print("✅ Puedes ejecutar el backtesting sin problemas")
        print("\n🚀 Próximos pasos:")
        print("   python main.py --config  # Ver configuración")
        print("   python main.py           # Ejecutar backtest")
    else:
        print("❌ ALGUNOS ARCHIVOS TIENEN PROBLEMAS")
        print("💡 Soluciones:")
        print("   1. Verificar que los archivos CSV existen en data/")
        print("   2. Verificar que tienen las columnas correctas")
        print("   3. Actualizar rutas en config.py si es necesario")
    
    print("="*60)
    
    return all_valid

def suggest_file_names():
    """Sugiere nombres de archivos según el instrumento activo"""
    print(f"\n💡 SUGERENCIAS PARA {ACTIVE_INSTRUMENT}:")
    print(f"   Archivo 15M: data/{ACTIVE_INSTRUMENT}_15M.csv")
    print(f"   Archivo 4H:  data/{ACTIVE_INSTRUMENT}_4H.csv")
    
    print(f"\n📋 Para cambiar archivos, edita config.py:")
    print(f'   DATA_CONFIG["csv_file_path_15m"] = "data/tu_archivo_15m.csv"')
    print(f'   DATA_CONFIG["csv_file_path_4h"] = "data/tu_archivo_4h.csv"')

def main():
    """Función principal"""
    valid = validate_data_files()
    
    if not valid:
        suggest_file_names()
        
        # Preguntar si quiere actualizar config
        print(f"\n❓ ¿Quieres que te ayude a configurar las rutas correctas?")
        help_config = input("   (y/n): ").lower().strip()
        
        if help_config == 'y':
            print(f"\n📝 CONFIGURACIÓN ASISTIDA:")
            
            # Listar archivos CSV en data/
            data_dir = "data"
            if os.path.exists(data_dir):
                csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
                if csv_files:
                    print(f"\n📁 Archivos CSV encontrados en {data_dir}/:")
                    for i, file in enumerate(csv_files, 1):
                        print(f"   {i}. {file}")
                    
                    print(f"\n💡 Ejemplo de configuración en config.py:")
                    if len(csv_files) >= 2:
                        print(f'   DATA_CONFIG["csv_file_path_15m"] = "data/{csv_files[0]}"')
                        print(f'   DATA_CONFIG["csv_file_path_4h"] = "data/{csv_files[1]}"')
                else:
                    print(f"   ❌ No se encontraron archivos CSV en {data_dir}/")
            else:
                print(f"   ❌ Directorio {data_dir}/ no existe")

if __name__ == "__main__":
    main()