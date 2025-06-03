# main.py - Script Principal para ejecutar el CFD Backtest

import sys
import os
from datetime import datetime

# Importar el motor de backtesting
from cfd_backtest_engine import run_cfd_backtest
from config import ACTIVE_INSTRUMENT, CAPITAL_CONFIG, print_current_config

def main():
    """Función principal"""
    print("="*70)
    print("CFD BACKTESTING SYSTEM")
    print("="*70)
    print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Instrumento activo: {ACTIVE_INSTRUMENT}")
    
    try:
        # Mostrar configuración actual
        print("\n" + "="*50)
        print("CONFIGURACIÓN ACTUAL")
        print("="*50)
        print_current_config()
        
        # Confirmación del usuario
        print("\n" + "="*50)
        print("CONFIRMACIÓN")
        print("="*50)
        
        confirm = input("\n¿Deseas ejecutar el backtest con esta configuración? (y/n): ").lower().strip()
        
        if confirm != 'y':
            print("❌ Backtest cancelado por el usuario")
            return
        
        print("\n🚀 Iniciando backtest...")
        
        # Ejecutar backtest
        results = run_cfd_backtest()
        
        if results is None:
            print("❌ Error: El backtest no pudo completarse")
            return
        
        # Mostrar resumen final
        print_final_summary(results)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Backtest interrumpido por el usuario")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado - {e}")
        print("Verifica que los archivos CSV estén en la ruta correcta")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n" + "="*70)
        print("FIN DE EJECUCIÓN")
        print("="*70)

def print_final_summary(results):
    """Imprime un resumen final de los resultados"""
    print("\n" + "🏆" + "="*60)
    print("RESUMEN FINAL DEL BACKTEST")
    print("="*61)
    
    # Métricas básicas
    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   Total de trades ejecutados: {results['total_trades']}")
    print(f"   Tasa de acierto: {results['win_rate']:.1f}%")
    print(f"   Instrumento: {ACTIVE_INSTRUMENT}")
    
    # Rentabilidad
    initial_capital = CAPITAL_CONFIG['initial_capital']
    final_capital = results['final_capital']
    roi_percent = ((final_capital / initial_capital) - 1) * 100
    
    print(f"\n💰 RENTABILIDAD:")
    print(f"   Capital inicial: ${initial_capital:,.2f}")
    print(f"   Capital final: ${final_capital:,.2f}")
    print(f"   Beneficio/Pérdida: ${results['total_profit']:,.2f}")
    print(f"   ROI: {roi_percent:+.1f}%")
    
    # Métricas de riesgo
    print(f"\n⚖️  MÉTRICAS DE RIESGO:")
    print(f"   Profit Factor: {results['profit_factor']:.2f}")
    print(f"   Máximo Drawdown: {results['max_drawdown']:.1f}%")
    
    # Evaluación del resultado
    print(f"\n🎯 EVALUACIÓN:")
    if results['total_trades'] == 0:
        print("   ❌ No se ejecutaron trades - Revisar filtros y configuración")
    elif results['profit_factor'] > 1.5 and results['win_rate'] > 40:
        print("   ✅ Estrategia prometedora - Resultados positivos")
    elif results['profit_factor'] > 1.0:
        print("   ⚠️  Estrategia marginal - Considerar optimización")
    else:
        print("   ❌ Estrategia no rentable - Requiere revisión completa")
    
    # Recomendaciones
    print(f"\n💡 RECOMENDACIONES:")
    
    if results['total_trades'] < 30:
        print("   • Período de prueba muy corto, considerar más datos")
    
    if results['win_rate'] < 35:
        print("   • Tasa de acierto baja, revisar filtros de entrada")
    
    if results['max_drawdown'] > 20:
        print("   • Drawdown elevado, considerar reducir riesgo por trade")
    
    if results['profit_factor'] < 1.2:
        print("   • Profit factor bajo, optimizar salidas y gestión de riesgo")
    
    # Archivos generados
    print(f"\n📁 ARCHIVOS GENERADOS:")
    print(f"   • Resultados detallados en: results/")
    print(f"   • Gráfica de equity en: results/")
    
    print("\n" + "="*61)

def show_help():
    """Muestra ayuda sobre el uso del script"""
    print("""
CFD BACKTESTING SYSTEM - AYUDA

DESCRIPCIÓN:
    Sistema de backtesting para CFDs con indicadores Ichimoku y filtros avanzados.

USO:
    python main.py              # Ejecuta backtest con configuración actual
    python main.py --help       # Muestra esta ayuda
    python main.py --config     # Muestra solo la configuración actual

CONFIGURACIÓN:
    Edita el archivo 'config.py' para cambiar:
    - Instrumento (UK100, WallStreet30, Germany40)
    - Capital inicial y riesgo por trade
    - Filtros técnicos y umbrales
    - Horarios de trading
    - Parámetros de Ichimoku

ARCHIVOS REQUERIDOS:
    - config.py                 # Configuración del sistema
    - cfd_backtest_engine.py    # Motor de backtesting
    - data/[INSTRUMENTO]_15M.csv   # Datos de 15 minutos
    - data/[INSTRUMENTO]_4H.csv    # Datos de 4 horas

RESULTADOS:
    Los resultados se guardan automáticamente en el directorio 'results/'
    incluyendo trades detallados y gráficas de equity.

EJEMPLOS:
    # Cambiar instrumento en config.py
    ACTIVE_INSTRUMENT = "WallStreet30"
    
    # Ajustar riesgo
    CAPITAL_CONFIG["risk_per_trade"] = 20
    
    # Desactivar filtro de volumen
    FILTERS_CONFIG["use_volume_filter"] = False

Para más información, consulta los comentarios en config.py
    """)

if __name__ == "__main__":
    # Verificar argumentos de línea de comandos
    if len(sys.argv) > 1:
        if sys.argv[1] in ['--help', '-h']:
            show_help()
        elif sys.argv[1] in ['--config', '-c']:
            print_current_config()
        else:
            print(f"Argumento no reconocido: {sys.argv[1]}")
            print("Usa --help para ver las opciones disponibles")
    else:
        # Ejecutar backtest normal
        main()