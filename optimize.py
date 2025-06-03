# optimize.py - Script de Optimización de Parámetros para CFD Backtest

import pandas as pd
import numpy as np
import itertools
from datetime import datetime
import os

from cfd_backtest_engine import CFDBacktestEngine
from config import print_current_config, validate_config
from config import *

class CFDOptimizer:
    def __init__(self):
        """Inicializa el optimizador"""
        self.results = []
        self.best_result = None

    def run_optimization(self, parameter_ranges=None, optimization_metric="profit_factor"):
        """
        Ejecuta optimización de parámetros

        Args:
            parameter_ranges: Dict con rangos de parámetros a optimizar
            optimization_metric: Métrica a optimizar ('profit_factor', 'sharpe_ratio', 'win_rate', 'total_profit')
        """
        print("="*70)
        print("CFD PARAMETER OPTIMIZATION")
        print("="*70)

        # Usar rangos por defecto si no se especifican
        if parameter_ranges is None:
            parameter_ranges = OPTIMIZATION_CONFIG["parameter_ranges"]

        # Generar combinaciones de parámetros
        param_combinations = self._generate_parameter_combinations(parameter_ranges)
        total_combinations = len(param_combinations)

        print(f"Instrumento: {ACTIVE_INSTRUMENT}")
        print(f"Total de combinaciones a probar: {total_combinations}")
        print(f"Métrica de optimización: {optimization_metric}")
        print(f"Mínimo trades requeridos: {OPTIMIZATION_CONFIG['min_trades_for_valid_result']}")

        # Confirmar ejecución
        confirm = input(f"\n¿Continuar con la optimización? (y/n): ").lower().strip()
        if confirm != 'y':
            print("❌ Optimización cancelada")
            return None

        print("\n🚀 Iniciando optimización...")
        start_time = datetime.now()

        # Ejecutar optimización
        for i, params in enumerate(param_combinations):
            try:
                print(f"\n[{i+1}/{total_combinations}] Probando: {params}")

                # Actualizar configuración temporal
                self._update_config_temporarily(params)

                # Ejecutar backtest
                engine = CFDBacktestEngine()
                results = engine.run_backtest()

                # Validar que results no es None y tiene las claves necesarias
                if results is not None and 'total_trades' in results and 'win_rate' in results:
                    # Validar resultados
                    if results['total_trades'] >= OPTIMIZATION_CONFIG['min_trades_for_valid_result']:
                        # Agregar parámetros a los resultados
                        results.update(params)
                        results['combination_id'] = i + 1
                        self.results.append(results)

                        # Verificar que la métrica existe en results
                        if optimization_metric in results:
                            metric_value = results[optimization_metric]
                            print(f"✅ Válido - Trades: {results['total_trades']}, "
                                  f"{optimization_metric}: {metric_value:.2f}")
                        else:
                            print(f"⚠️ Métrica {optimization_metric} no encontrada en resultados")
                    else:
                        print(f"❌ Insuficientes trades: {results['total_trades']}")
                else:
                    print(f"❌ Error: Resultados inválidos o None")

                # Mostrar progreso
                elapsed = datetime.now() - start_time
                avg_time = elapsed / (i + 1)
                eta = avg_time * (total_combinations - i - 1)
                print(f"   Progreso: {((i+1)/total_combinations)*100:.1f}% - ETA: {eta}")

            except Exception as e:
                print(f"❌ Error en combinación {i+1}: {e}")
                continue

        # Analizar resultados
        total_time = datetime.now() - start_time
        print(f"\n✅ Optimización completada en {total_time}")
        print(f"Combinaciones válidas: {len(self.results)}/{total_combinations}")

        if self.results:
            self._analyze_results(optimization_metric)
            self._save_optimization_results()
            return self.best_result
        else:
            print("❌ No se obtuvieron resultados válidos")
            return None

    def _generate_parameter_combinations(self, parameter_ranges):
        """Genera todas las combinaciones de parámetros"""
        param_names = list(parameter_ranges.keys())
        param_values = []

        for param_name in param_names:
            range_config = parameter_ranges[param_name]
            if len(range_config) == 3:  # (min, max, step)
                values = np.arange(range_config[0], range_config[1] + range_config[2], range_config[2])
                # Redondear para evitar problemas de float
                values = np.round(values, 6)
            else:  # Lista de valores específicos
                values = range_config

            param_values.append(values)

        # Generar todas las combinaciones
        combinations = list(itertools.product(*param_values))

        # Convertir a lista de diccionarios
        param_combinations = []
        for combo in combinations:
            param_dict = dict(zip(param_names, combo))
            param_combinations.append(param_dict)

        return param_combinations

    def _update_config_temporarily(self, params):
        """Actualiza temporalmente la configuración con los parámetros dados"""
        global FILTERS_CONFIG, RISK_CONFIG

        # Mapear parámetros a configuración
        if 'volume_threshold' in params:
            FILTERS_CONFIG['volume_threshold'] = params['volume_threshold']

        if 'atr_threshold' in params:
            FILTERS_CONFIG['atr_threshold'] = params['atr_threshold']

        if 'trailing_stop' in params:
            RISK_CONFIG['trailing_stop_percent'] = params['trailing_stop']

        if 'rsi_oversold' in params:
            FILTERS_CONFIG['rsi_oversold'] = params['rsi_oversold']

        if 'rsi_overbought' in params:
            FILTERS_CONFIG['rsi_overbought'] = params['rsi_overbought']

    def _analyze_results(self, optimization_metric):
        """Analiza y ordena los resultados"""
        # Convertir a DataFrame
        df_results = pd.DataFrame(self.results)

        # Verificar que la métrica existe en los resultados
        if optimization_metric not in df_results.columns:
            print(f"❌ Error: Métrica '{optimization_metric}' no encontrada en resultados")
            available_metrics = [col for col in df_results.columns if col in ['profit_factor', 'win_rate', 'total_profit']]
            print(f"Métricas disponibles: {available_metrics}")
            if available_metrics:
                optimization_metric = available_metrics[0]
                print(f"Usando métrica alternativa: {optimization_metric}")
            else:
                print("❌ No hay métricas válidas para analizar")
                return df_results

        # Ordenar por métrica de optimización (descendente)
        df_results = df_results.sort_values(optimization_metric, ascending=False)

        # Guardar el mejor resultado
        if not df_results.empty:
            self.best_result = df_results.iloc[0].to_dict()

            # Mostrar top 5 resultados
            print(f"\n🏆 TOP 5 RESULTADOS POR {optimization_metric.upper()}:")
            print("="*80)

            top_5 = df_results.head(5)
            for i, (idx, row) in enumerate(top_5.iterrows()):
                print(f"\n#{i+1} - Combinación {int(row.get('combination_id', i+1))}")
                print(f"   {optimization_metric}: {row[optimization_metric]:.3f}")
                print(f"   Total trades: {int(row.get('total_trades', 0))}")
                print(f"   Win rate: {row.get('win_rate', 0):.1f}%")
                print(f"   Total profit: ${row.get('total_profit', 0):.2f}")
                print(f"   Max drawdown: {row.get('max_drawdown', 0):.1f}%")

                # Mostrar parámetros
                param_str = []
                for param in ['volume_threshold', 'atr_threshold', 'trailing_stop']:
                    if param in row and pd.notna(row[param]):
                        param_str.append(f"{param}: {row[param]:.3f}")
                if param_str:
                    print(f"   Parámetros: {', '.join(param_str)}")

            # Estadísticas generales
            print(f"\n📊 ESTADÍSTICAS DE OPTIMIZACIÓN:")
            print(f"   Mejor {optimization_metric}: {df_results[optimization_metric].max():.3f}")
            print(f"   Promedio {optimization_metric}: {df_results[optimization_metric].mean():.3f}")
            print(f"   Desviación estándar: {df_results[optimization_metric].std():.3f}")

            # Verificar si hay columna total_profit
            if 'total_profit' in df_results.columns:
                profitable_count = len(df_results[df_results['total_profit'] > 0])
                print(f"   Resultados rentables: {profitable_count}/{len(df_results)}")

            # Análisis de sensibilidad
            self._sensitivity_analysis(df_results)

        return df_results

    def _sensitivity_analysis(self, df_results):
        """Realiza análisis de sensibilidad de parámetros"""
        print(f"\n🔍 ANÁLISIS DE SENSIBILIDAD:")
        print("="*50)

        param_columns = ['volume_threshold', 'atr_threshold', 'trailing_stop']

        # Verificar que profit_factor existe
        if 'profit_factor' not in df_results.columns:
            print("❌ No se puede realizar análisis de sensibilidad: 'profit_factor' no encontrado")
            return

        for param in param_columns:
            if param in df_results.columns:
                try:
                    # Correlación con profit factor
                    correlation = df_results[param].corr(df_results['profit_factor'])

                    # Mejor valor del parámetro
                    best_idx = df_results['profit_factor'].idxmax()
                    best_value = df_results.loc[best_idx, param]

                    # Rango de valores probados
                    min_val = df_results[param].min()
                    max_val = df_results[param].max()

                    print(f"\n{param.replace('_', ' ').title()}:")
                    if pd.notna(correlation):
                        print(f"   Correlación con Profit Factor: {correlation:+.3f}")
                    else:
                        print(f"   Correlación con Profit Factor: No calculable")

                    if pd.notna(best_value):
                        print(f"   Mejor valor: {best_value:.3f}")
                    print(f"   Rango probado: {min_val:.3f} - {max_val:.3f}")

                    # Interpretación
                    if pd.notna(correlation):
                        if abs(correlation) > 0.5:
                            direction = "positiva" if correlation > 0 else "negativa"
                            print(f"   ➤ Correlación {direction} fuerte - Parámetro importante")
                        elif abs(correlation) > 0.3:
                            direction = "positiva" if correlation > 0 else "negativa"
                            print(f"   ➤ Correlación débil - Parámetro menos crítico")

                except Exception as e:
                    print(f"   ❌ Error analizando {param}: {e}")
            else:
                print(f"\n{param.replace('_', ' ').title()}:")
                print(f"   ❌ Parámetro no encontrado en resultados")

        return

    def _save_optimization_results(self):
        """Guarda los resultados de optimización"""
        # Crear directorio si no existe
        os.makedirs(LOGGING_CONFIG["output_directory"], exist_ok=True)

        # Guardar resultados completos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{LOGGING_CONFIG['output_directory']}optimization_{ACTIVE_INSTRUMENT}_{timestamp}.csv"

        df_results = pd.DataFrame(self.results)
        df_results.to_csv(filename, index=False)

        print(f"\n💾 Resultados de optimización guardados en: {filename}")

        # Guardar configuración del mejor resultado
        best_config_file = f"{LOGGING_CONFIG['output_directory']}best_config_{ACTIVE_INSTRUMENT}_{timestamp}.txt"
        if self.best_result:
            self._save_best_config(best_config_file)
            print(f"💾 Mejor configuración guardada en: {best_config_file}")
        else:
            print("❌ No best result to save.")

    def _save_best_config(self, filename):
        """Guarda la configuración del mejor resultado"""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# MEJOR CONFIGURACIÓN ENCONTRADA\n")
            f.write("# Generado por optimización automática\n")
            f.write(f"# Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Instrumento: {ACTIVE_INSTRUMENT}\n\n")

            f.write("# RESULTADOS:\n")
            if self.best_result is not None:
                if 'total_trades' in self.best_result and hasattr(self.best_result, 'total_trades'):
                    f.write(f"# Total trades: {self.best_result['total_trades']}\n")
                else:
                    f.write("# Total trades: N/A\n")
                if 'win_rate' in self.best_result and hasattr(self.best_result, 'win_rate'):
                    f.write(f"# Win rate: {self.best_result['win_rate']:.2f}%\n")
                else:
                    f.write("# Win rate: N/A\n")
                if 'profit_factor' in self.best_result and hasattr(self.best_result, 'profit_factor'):
                    f.write(f"# Profit factor: {self.best_result['profit_factor']:.3f}\n")
                else:
                    f.write("# Profit factor: N/A\n")
                if 'total_profit' in self.best_result and hasattr(self.best_result, 'total_profit'):
                    f.write(f"# Total profit: ${self.best_result['total_profit']:.2f}\n")
                else:
                    f.write("# Total profit: N/A\n")
                if 'max_drawdown' in self.best_result and hasattr(self.best_result, 'max_drawdown'):
                    f.write(f"# Max drawdown: {self.best_result['max_drawdown']:.2f}%\n\n")
                else:
                    f.write("# Max drawdown: N/A\n\n")

                f.write("# PARÁMETROS ÓPTIMOS:\n")
                if 'volume_threshold' in self.best_result and hasattr(self.best_result, 'volume_threshold'):
                    f.write(f"FILTERS_CONFIG['volume_threshold'] = {self.best_result['volume_threshold']}\n")
                else:
                    f.write("FILTERS_CONFIG['volume_threshold'] = N/A\n")
                if 'atr_threshold' in self.best_result and hasattr(self.best_result, 'atr_threshold'):
                    f.write(f"FILTERS_CONFIG['atr_threshold'] = {self.best_result['atr_threshold']}\n")
                else:
                    f.write("FILTERS_CONFIG['atr_threshold'] = N/A\n")
                if 'trailing_stop' in self.best_result and hasattr(self.best_result, 'trailing_stop'):
                    f.write(f"RISK_CONFIG['trailing_stop_percent'] = {self.best_result['trailing_stop']}\n")
            else:
                f.write("# No best result found.\n")

def run_quick_optimization():
    """Ejecuta una optimización rápida con rangos reducidos"""
    print("🚀 OPTIMIZACIÓN RÁPIDA")
    
    # Rangos reducidos para optimización rápida
    quick_ranges = {
        'volume_threshold': (1.1, 1.5, 0.2),
        'atr_threshold': (1.0, 1.4, 0.2),
        'trailing_stop': (0.015, 0.025, 0.005)
    }
    
    optimizer = CFDOptimizer()
    return optimizer.run_optimization(quick_ranges, "profit_factor")

def run_full_optimization():
    """Ejecuta una optimización completa con rangos amplios"""
    print("🔥 OPTIMIZACIÓN COMPLETA")
    
    # Usar rangos de configuración completos
    optimizer = CFDOptimizer()
    return optimizer.run_optimization(OPTIMIZATION_CONFIG["parameter_ranges"], "profit_factor")

def run_custom_optimization():
    """Permite al usuario definir rangos personalizados"""
    print("⚙️  OPTIMIZACIÓN PERSONALIZADA")
    print("\nDefinir rangos de parámetros:")
    
    custom_ranges = {}
    
    # Volume threshold
    print(f"\n1. Volume Threshold (actual: {FILTERS_CONFIG['volume_threshold']})")
    min_vol = float(input("   Mínimo (ej: 1.0): ") or "1.0")
    max_vol = float(input("   Máximo (ej: 2.0): ") or "2.0")
    step_vol = float(input("   Paso (ej: 0.2): ") or "0.2")
    custom_ranges['volume_threshold'] = (min_vol, max_vol, step_vol)
    
    # ATR threshold
    print(f"\n2. ATR Threshold (actual: {FILTERS_CONFIG['atr_threshold']})")
    min_atr = float(input("   Mínimo (ej: 0.8): ") or "0.8")
    max_atr = float(input("   Máximo (ej: 1.6): ") or "1.6")
    step_atr = float(input("   Paso (ej: 0.2): ") or "0.2")
    custom_ranges['atr_threshold'] = (min_atr, max_atr, step_atr)
    
    # Trailing stop
    print(f"\n3. Trailing Stop (actual: {RISK_CONFIG['trailing_stop_percent']})")
    min_ts = float(input("   Mínimo (ej: 0.01): ") or "0.01")
    max_ts = float(input("   Máximo (ej: 0.04): ") or "0.04")
    step_ts = float(input("   Paso (ej: 0.005): ") or "0.005")
    custom_ranges['trailing_stop'] = (min_ts, max_ts, step_ts)
    
    # Métrica de optimización
    print(f"\n4. Métrica de optimización:")
    print("   1) profit_factor (recomendado)")
    print("   2) total_profit")
    print("   3) win_rate")
    print("   4) sharpe_ratio")
    
    metric_choice = input("\nElegir opción (1-4): ").strip() or "1"
    metrics = {
        "1": "profit_factor",
        "2": "total_profit", 
        "3": "win_rate",
        "4": "sharpe_ratio"
    }
    metric = metrics.get(metric_choice, "profit_factor")
    
    print(f"\n📋 Resumen de optimización personalizada:")
    print(f"   Volume threshold: {custom_ranges['volume_threshold']}")
    print(f"   ATR threshold: {custom_ranges['atr_threshold']}")
    print(f"   Trailing stop: {custom_ranges['trailing_stop']}")
    print(f"   Métrica: {metric}")
    
    total_combinations = 1
    for param_range in custom_ranges.values():
        total_combinations *= len(np.arange(param_range[0], param_range[1] + param_range[2], param_range[2]))
    
    print(f"   Total combinaciones: {total_combinations}")
    
    optimizer = CFDOptimizer()
    return optimizer.run_optimization(custom_ranges, metric)

def main():
    """Función principal del script de optimización"""
    print("="*70)
    print("CFD PARAMETER OPTIMIZER")
    print("="*70)
    
    print("\nTipos de optimización disponibles:")
    print("1) Optimización rápida (~20 combinaciones)")
    print("2) Optimización completa (~100+ combinaciones)")
    print("3) Optimización personalizada")
    print("4) Mostrar configuración actual")
    print("5) Salir")
    
    while True:
        choice = input("\nElegir opción (1-5): ").strip()
        
        if choice == "1":
            result = run_quick_optimization()
            break
        elif choice == "2":
            result = run_full_optimization()
            break
        elif choice == "3":
            result = run_custom_optimization()
            break
        elif choice == "4":
            print_current_config()
            continue
        elif choice == "5":
            print("👋 Saliendo...")
            return
        else:
            print("❌ Opción inválida. Elegir 1-5.")
            continue
    
    if result:
        print("\n🎉 ¡Optimización completada exitosamente!")
        print("💡 Revisa los archivos generados en el directorio 'results/'")
        print("💡 Puedes copiar la mejor configuración a config.py")
    else:
        print("\n❌ La optimización no produjo resultados válidos")
        print("💡 Considera ajustar los rangos o filtros de configuración")

if __name__ == "__main__":
    main()
