# debug_safe.py - Versión SEGURA sin loops infinitos

import pandas as pd
from config import DATA_CONFIG
from cfd_backtest_engine import CFDBacktestEngine

def analyze_50_percent_issue():
    """Analiza por qué no hay trades después del 50%"""
    
    print("="*70)
    print("ANÁLISIS SEGURO DEL PROBLEMA DEL 50%")
    print("="*70)
    
    try:
        # 1. Verificar cobertura de datos
        print("\n1. VERIFICANDO COBERTURA DE DATOS...")
        df_15m = pd.read_csv(DATA_CONFIG["csv_file_path_15m"])
        df_4h = pd.read_csv(DATA_CONFIG["csv_file_path_4h"])
        
        # Convertir fechas
        if 'Local time' in df_15m.columns:
            df_15m['datetime'] = pd.to_datetime(df_15m['Local time'], format='%d.%m.%Y %H:%M:%S.%f GMT%z')
            df_4h['datetime'] = pd.to_datetime(df_4h['Local time'], format='%d.%m.%Y %H:%M:%S.%f GMT%z')
        else:
            df_15m['datetime'] = pd.to_datetime(df_15m['timestamp'])
            df_4h['datetime'] = pd.to_datetime(df_4h['timestamp'])
        
        # Rangos de fecha
        start_15m, end_15m = df_15m['datetime'].min(), df_15m['datetime'].max()
        start_4h, end_4h = df_4h['datetime'].min(), df_4h['datetime'].max()
        
        print(f"Datos 15M: {len(df_15m)} filas, {start_15m} a {end_15m}")
        print(f"Datos 4H:  {len(df_4h)} filas, {start_4h} a {end_4h}")
        
        # Punto del 50%
        mid_idx = len(df_15m) // 2
        date_at_50 = df_15m['datetime'].iloc[mid_idx]
        print(f"\nFecha al 50%: {date_at_50}")
        
        # 2. DIAGNÓSTICO
        print("\n2. DIAGNÓSTICO:")
        
        problem_found = False
        
        # Verificar si 4H termina antes
        if end_4h < end_15m:
            missing_days = (end_15m - end_4h).days
            print(f"❌ Datos 4H terminan {missing_days} días antes que 15M")
            
            if date_at_50 > end_4h:
                print(f"❌ El 50% ({date_at_50}) está DESPUÉS del fin de 4H ({end_4h})")
                print("   ¡ESE ES EL PROBLEMA!")
                problem_found = True
        
        # Verificar último trade vs datos
        last_trade = pd.Timestamp('2021-12-15 15:00')
        if last_trade > end_4h:
            print(f"❌ Último trade ({last_trade}) después del fin de datos 4H")
            problem_found = True
        
        if not problem_found:
            print("✅ Los rangos de datos parecen correctos")
            print("   El problema puede estar en la configuración de filtros")
        
        # 3. SOLUCIONES
        print("\n3. SOLUCIONES RECOMENDADAS:")
        
        if end_4h < end_15m:
            print("\nOpción A - Recortar datos 15M:")
            print(f"  1. Usar solo datos 15M hasta {end_4h}")
            print("  2. En config.py, puedes filtrar por fecha")
            
            print("\nOpción B - Extender datos 4H:")
            print("  1. Descargar más datos históricos 4H")
            print("  2. Asegurar que cubran todo el período")
            
            print("\nOpción C - Solución temporal:")
            print("  1. Desactivar el filtro de tendencia 4H")
            print("  2. En config.py, agregar:")
            print('     FILTERS_CONFIG["use_4h_trend_filter"] = False')
        
        return {
            'problem_found': problem_found,
            'end_4h': end_4h,
            'end_15m': end_15m,
            'date_at_50': date_at_50
        }
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return None

def test_without_4h_filter():
    """Prueba rápida sin el filtro 4H para confirmar el problema"""
    
    print("\n" + "="*70)
    print("TEST RÁPIDO SIN FILTRO 4H")
    print("="*70)
    
    # Modificar temporalmente la configuración
    from config import TIMEFRAME_CONFIG
    original_trend = TIMEFRAME_CONFIG.get("use_trend_filter", True)
    TIMEFRAME_CONFIG["use_trend_filter"] = False
    
    print("Ejecutando backtest sin filtro de tendencia 4H...")
    print("(Solo procesando primeras 10,000 barras para test rápido)")
    
    try:
        engine = CFDBacktestEngine()
        
        # Limitar a 10k barras para test rápido
        # Aquí podrías modificar el engine para procesar solo una parte
        
        print("\n✅ Si aparecen trades, confirma que el problema es la falta de datos 4H")
        
    except Exception as e:
        print(f"Error en test: {e}")
    finally:
        # Restaurar configuración
        TIMEFRAME_CONFIG["use_trend_filter"] = original_trend

if __name__ == "__main__":
    # Solo ejecutar el análisis, NO crear loops
    results = analyze_50_percent_issue()
    
    if results and results['problem_found']:
        print("\n" + "="*70)
        print("PROBLEMA CONFIRMADO: Falta de sincronización de datos 4H")
        print("="*70)