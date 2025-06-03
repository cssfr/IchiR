# cfd_backtest_engine.py - Motor de Backtesting para CFDs con filtros avanzados

import pandas as pd
import numpy as np
import ta.trend
import ta.volatility
import ta.momentum
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import os
from config import *

class CFDBacktestEngine:
    def __init__(self):
        """Inicializa el motor de backtesting"""
        self.instrument_config = get_active_instrument_config()
        self.reset_backtest_state()
        
    def reset_backtest_state(self):
        """Resetea el estado del backtest"""
        self.in_position = False
        self.entry_price = 0
        self.stop_loss = 0
        self.position_type = None
        self.position_size = 0
        self.entry_time = None
        self.trades = []
        self.capital = CAPITAL_CONFIG["initial_capital"]
        self.max_capital = CAPITAL_CONFIG["initial_capital"]
        self.consecutive_losses = 0
        self.trades_today = 0
        self.last_trade_time = None
        self.last_trade_direction = None

    def calculate_indicators(self, df):
        """Calcula todos los indicadores técnicos necesarios"""
        print("Calculando indicadores técnicos...")
        
        # Verificar datos suficientes
        min_periods = max(
            ICHIMOKU_CONFIG["senkou_periods"],
            FILTERS_CONFIG["volume_sma_periods"],
            FILTERS_CONFIG["atr_periods"]
        )
        
        if len(df) < min_periods:
            raise ValueError(f"Datos insuficientes. Se necesitan al menos {min_periods} períodos.")

        # Limpiar datos
        df['volume'] = df['volume'].fillna(0).clip(lower=0)
        
        # Indicadores Ichimoku
        ichimoku = ta.trend.IchimokuIndicator(
            high=df['high'], 
            low=df['low'],
            window1=ICHIMOKU_CONFIG["tenkan_periods"],
            window2=ICHIMOKU_CONFIG["kijun_periods"], 
            window3=ICHIMOKU_CONFIG["senkou_periods"]
        )
        
        df['tenkan_sen'] = ichimoku.ichimoku_conversion_line()
        df['kijun_sen'] = ichimoku.ichimoku_base_line()
        df['senkou_span_a'] = ichimoku.ichimoku_a()
        df['senkou_span_b'] = ichimoku.ichimoku_b()
        df['chikou_span'] = df['close'].shift(-ICHIMOKU_CONFIG["kijun_periods"])
        
        # Indicadores adicionales
        df['atr'] = ta.volatility.average_true_range(
            df['high'], df['low'], df['close'], 
            window=FILTERS_CONFIG["atr_periods"]
        )
        
        df['volume_sma'] = df['volume'].rolling(
            window=FILTERS_CONFIG["volume_sma_periods"]
        ).mean()
        
        df['rsi'] = ta.momentum.rsi(
            df['close'], 
            window=FILTERS_CONFIG["rsi_periods"]
        )
        
        # Limpiar NaN
        df['atr'] = df['atr'].fillna(df['atr'].mean())
        df['rsi'] = df['rsi'].fillna(50)
        df['volume_sma'] = df['volume_sma'].fillna(df['volume'])
        
        return df

    def is_trading_hours(self, timestamp):
        """Verifica si estamos en horario de trading"""
        if not FILTERS_CONFIG["use_trading_hours_filter"]:
            return True
            
        hours_config = self.instrument_config["trading_hours"]
        current_hour = timestamp.hour
        current_minute = timestamp.minute
        
        start_time = hours_config["start_hour"] * 60 + hours_config["start_minute"]
        end_time = hours_config["end_hour"] * 60 + hours_config["end_minute"]
        current_time = current_hour * 60 + current_minute
        
        # Manejar casos donde el mercado cruza medianoche
        if start_time > end_time:  # Ej: 23:00 a 21:00 del día siguiente
            return current_time >= start_time or current_time <= end_time
        else:  # Caso normal: 08:00 a 16:30
            return start_time <= current_time <= end_time

    def validate_stop_distance(self, entry_price, stop_loss_price):
        """Valida que la distancia del stop loss esté en rango permitido"""
        if not FILTERS_CONFIG["use_stop_distance_filter"]:
            return True, "Stop distance filter disabled"
            
        distance = abs(entry_price - stop_loss_price)
        min_distance = self.instrument_config["stop_limits"]["min_stop_distance"]
        max_distance = self.instrument_config["stop_limits"]["max_stop_distance"]
        
        if distance < min_distance:
            return False, f"Stop muy cercano: {distance:.1f} < {min_distance} puntos"
        
        if distance > max_distance:
            return False, f"Stop muy lejano: {distance:.1f} > {max_distance} puntos"
        
        return True, "Stop distance válida"

    def check_spread_conditions(self, df, i):
        """Verifica las condiciones de spread"""
        if not FILTERS_CONFIG["use_spread_filter"]:
            return True
            
        # Simular spread variable basado en volatilidad
        base_spread = self.instrument_config["spread"]
        atr = df['atr'].iloc[i]
        atr_avg = df['atr'].iloc[max(0, i-20):i].mean()
        
        # Spread aumenta con volatilidad
        volatility_multiplier = max(1.0, atr / atr_avg) if atr_avg > 0 else 1.0
        current_spread = base_spread * volatility_multiplier
        max_allowed_spread = base_spread * FILTERS_CONFIG["max_spread_multiplier"]
        
        return current_spread <= max_allowed_spread

    def analyze_market_conditions(self, df, i):
        """Analiza las condiciones del mercado"""
        try:
            conditions = {}
            
            # Condiciones de volumen
            if FILTERS_CONFIG["use_volume_filter"]:
                volume = df['volume'].iloc[i]
                volume_sma = df['volume_sma'].iloc[i]
                volume_ratio = volume / volume_sma if volume_sma > 0 else 1.0
                conditions['volume_surge'] = volume_ratio > FILTERS_CONFIG["volume_threshold"]
            else:
                conditions['volume_surge'] = True
            
            # Condiciones de ATR
            if FILTERS_CONFIG["use_atr_filter"]:
                atr_current = df['atr'].iloc[i]
                atr_previous = df['atr'].iloc[i-1] if i > 0 else atr_current
                atr_ratio = atr_current / atr_previous if atr_previous > 0 else 1.0
                conditions['atr_increasing'] = atr_ratio > FILTERS_CONFIG["atr_threshold"]
            else:
                conditions['atr_increasing'] = True
            
            # Condiciones de RSI
            if FILTERS_CONFIG["use_rsi_filter"]:
                rsi = df['rsi'].iloc[i]
                conditions['rsi_not_overbought'] = rsi < FILTERS_CONFIG["rsi_overbought"]
                conditions['rsi_not_oversold'] = rsi > FILTERS_CONFIG["rsi_oversold"]
            else:
                conditions['rsi_not_overbought'] = True
                conditions['rsi_not_oversold'] = True
            
            return conditions
            
        except Exception as e:
            print(f"Error en analyze_market_conditions: {e}")
            return {'volume_surge': False, 'atr_increasing': False, 
                   'rsi_not_overbought': False, 'rsi_not_oversold': False}

    def check_risk_management_rules(self, current_time):
        """Verifica las reglas de gestión de riesgo"""
        # Verificar pérdidas consecutivas
        if self.consecutive_losses >= RISK_CONFIG["max_consecutive_losses"]:
            return False, f"Máximo de pérdidas consecutivas alcanzado: {self.consecutive_losses}"
        
        # Verificar trades por día
        if self.last_trade_time and current_time.date() == self.last_trade_time.date():
            if self.trades_today >= RISK_CONFIG["max_trades_per_day"]:
                return False, f"Máximo trades por día alcanzado: {self.trades_today}"
        else:
            self.trades_today = 0  # Nuevo día
        
        # Verificar cooldown entre trades
        if (self.last_trade_time and 
            (current_time - self.last_trade_time).total_seconds() < RISK_CONFIG["cooldown_minutes"] * 60):
            return False, "En período de cooldown"
        
        # Verificar capital mínimo
        if self.capital < CAPITAL_CONFIG["min_capital_required"]:
            return False, f"Capital insuficiente: ${self.capital:.2f}"
        
        return True, "Risk management OK"

    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calcula el tamaño de posición para CFDs"""
        risk_distance = abs(entry_price - stop_loss_price)
        unit_value = self.instrument_config["unit_value"]
        
        # Calcular riesgo por unidad
        risk_per_unit = risk_distance * unit_value
        
        if risk_per_unit <= 0:
            return 0, 0
        
        # Calcular número de unidades
        position_size_exact = CAPITAL_CONFIG["risk_per_trade"] / risk_per_unit
        
        # Redondear a múltiplos del tamaño mínimo
        min_size = self.instrument_config["min_position_size"]
        position_size = round(position_size_exact / min_size) * min_size
        
        # Verificar tamaño mínimo
        if position_size < min_size:
            return 0, 0
        
        # Calcular valor nominal
        nominal_value = position_size * unit_value
        
        # Verificar margen disponible
        required_margin = nominal_value * self.instrument_config["margin_requirement"]
        if required_margin > self.capital * 0.8:  # Usar máximo 80% del capital como margen
            return 0, 0
        
        return position_size, nominal_value

    def apply_spread_cost(self, entry_price, position_type):
        """Aplica el costo del spread al precio de entrada"""
        spread = self.instrument_config["spread"]
        
        if position_type == 'long':
            # Long: compramos al ask (precio + spread/2)
            return entry_price + (spread / 2)
        else:
            # Short: vendemos al bid (precio - spread/2)
            return entry_price - (spread / 2)

    def get_4h_trend_bias(self, df_4h, current_time):
        """Obtiene la tendencia del timeframe de 4H"""
        try:
            # Encontrar la barra de 4H más reciente
            df_4h_relevant = df_4h[df_4h.index <= current_time]
            if df_4h_relevant.empty:
                return None
            
            latest_4h = df_4h_relevant.iloc[-1]
            current_price = latest_4h['close']
            
            # Determinar posición respecto a la nube
            cloud_top = max(latest_4h['senkou_span_a'], latest_4h['senkou_span_b'])
            cloud_bottom = min(latest_4h['senkou_span_a'], latest_4h['senkou_span_b'])
            
            if current_price > cloud_top:
                return 'bullish'
            elif current_price < cloud_bottom:
                return 'bearish'
            else:
                return 'neutral'
                
        except Exception as e:
            print(f"Error en get_4h_trend_bias: {e}")
            return None

    def check_ichimoku_signal(self, df, i, signal_type):
        """Verifica señales de Ichimoku en 15M"""
        try:
            # Verificar cruce de Tenkan y Kijun
            tenkan_current = df['tenkan_sen'].iloc[i]
            tenkan_previous = df['tenkan_sen'].iloc[i-1]
            kijun_current = df['kijun_sen'].iloc[i]
            kijun_previous = df['kijun_sen'].iloc[i-1]
            
            if signal_type == 'long':
                # Cruce alcista: Tenkan cruza por encima de Kijun
                return (tenkan_current > kijun_current and 
                       tenkan_previous <= kijun_previous)
            else:
                # Cruce bajista: Tenkan cruza por debajo de Kijun
                return (tenkan_current < kijun_current and 
                       tenkan_previous >= kijun_previous)
                       
        except Exception as e:
            print(f"Error en check_ichimoku_signal: {e}")
            return False

    def execute_trade_entry(self, df, i, df_4h, current_time, current_price):
        """Ejecuta la entrada de un trade"""
        # Verificar tendencia de 4H
        trend_bias = self.get_4h_trend_bias(df_4h, current_time)
        if trend_bias is None:
            return False
        
        # Verificar condiciones de mercado
        market_conditions = self.analyze_market_conditions(df, i)
        if not all(market_conditions.values()):
            return False
        
        # Verificar condiciones de spread
        if not self.check_spread_conditions(df, i):
            return False
        
        # Verificar reglas de gestión de riesgo
        risk_ok, risk_message = self.check_risk_management_rules(current_time)
        if not risk_ok:
            return False
        
        # Buscar señales según la tendencia
        signal_found = False
        position_type = None
        
        if trend_bias == 'bullish':
            if self.check_ichimoku_signal(df, i, 'long'):
                signal_found = True
                position_type = 'long'
        elif trend_bias == 'bearish':
            if self.check_ichimoku_signal(df, i, 'short'):
                signal_found = True
                position_type = 'short'
        
        if not signal_found:
            return False
        
        # Calcular stop loss
        if position_type == 'long':
            stop_loss_level = min(df['senkou_span_a'].iloc[i], df['senkou_span_b'].iloc[i])
        else:
            stop_loss_level = max(df['senkou_span_a'].iloc[i], df['senkou_span_b'].iloc[i])
        
        # Validar distancia del stop
        stop_valid, stop_message = self.validate_stop_distance(current_price, stop_loss_level)
        if not stop_valid:
            return False
        
        # Aplicar spread al precio de entrada
        entry_price_with_spread = self.apply_spread_cost(current_price, position_type)
        
        # Calcular tamaño de posición
        position_size, nominal_value = self.calculate_position_size(
            entry_price_with_spread, stop_loss_level
        )
        
        if position_size == 0:
            return False
        
        # Ejecutar entrada
        self.in_position = True
        self.entry_price = entry_price_with_spread
        self.stop_loss = stop_loss_level
        self.position_type = position_type
        self.position_size = position_size
        self.entry_time = current_time
        
        # Actualizar contadores
        self.trades_today += 1
        self.last_trade_time = current_time
        self.last_trade_direction = position_type
        
        # Log de entrada
        required_margin = nominal_value * self.instrument_config["margin_requirement"]
        spread_cost = abs(entry_price_with_spread - current_price)
        
        print(f"\n{position_type.upper() if position_type else 'UNKNOWN'} ENTRY - {current_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Price: {current_price:.1f} → Entry: {entry_price_with_spread:.1f} (Spread: {spread_cost:.1f})")
        print(f"Size: {position_size} units (${nominal_value:.2f} exposure)")
        print(f"Stop Loss: {stop_loss_level:.1f}")
        print(f"Margin Required: ${required_margin:.2f}")
        print(f"Trend Bias: {trend_bias}")
        
        return True

    def manage_open_position(self, current_price, current_time):
        """Gestiona una posición abierta"""
        exit_position = False
        exit_reason = None
        exit_price = current_price
        
        if self.position_type == 'long':
            # Aplicar spread en la salida (vendemos al bid)
            exit_price_with_spread = current_price - (self.instrument_config["spread"] / 2)
            
            # Verificar stop loss
            if exit_price_with_spread <= self.stop_loss:
                exit_position = True
                exit_reason = "Stop Loss"
                exit_price = self.stop_loss - (self.instrument_config["spread"] / 2)
            
            # Actualizar trailing stop si está activado
            elif RISK_CONFIG["use_trailing_stop"]:
                unrealized_profit = (exit_price_with_spread - self.entry_price) * self.position_size
                if unrealized_profit > 0:
                    trailing_distance = current_price * RISK_CONFIG["trailing_stop_percent"]
                    new_stop = current_price - trailing_distance
                    if new_stop > self.stop_loss:
                        self.stop_loss = new_stop
        
        else:  # short position
            # Aplicar spread en la salida (compramos al ask)
            exit_price_with_spread = current_price + (self.instrument_config["spread"] / 2)
            
            # Verificar stop loss
            if exit_price_with_spread >= self.stop_loss:
                exit_position = True
                exit_reason = "Stop Loss"
                exit_price = self.stop_loss + (self.instrument_config["spread"] / 2)
            
            # Actualizar trailing stop si está activado
            elif RISK_CONFIG["use_trailing_stop"]:
                unrealized_profit = (self.entry_price - exit_price_with_spread) * self.position_size
                if unrealized_profit > 0:
                    trailing_distance = current_price * RISK_CONFIG["trailing_stop_percent"]
                    new_stop = current_price + trailing_distance
                    if new_stop < self.stop_loss:
                        self.stop_loss = new_stop
        
        if exit_position:
            self.close_position(exit_price, current_time, exit_reason)
        
        return exit_position

    def close_position(self, exit_price, exit_time, exit_reason):
        """Cierra una posición abierta"""
        # Calcular P&L
        if self.position_type == 'long':
            profit_loss = (exit_price - self.entry_price) * self.position_size
        else:
            profit_loss = (self.entry_price - exit_price) * self.position_size
        
        # Calcular métricas del trade
        hold_time = (exit_time - self.entry_time).total_seconds() / 3600
        risk_multiple = profit_loss / CAPITAL_CONFIG["risk_per_trade"]
        
        # Registrar trade
        trade_data = {
            'entry_time': self.entry_time,
            'exit_time': exit_time,
            'type': self.position_type,
            'entry_price': self.entry_price,
            'exit_price': exit_price,
            'position_size': self.position_size,
            'profit_loss': profit_loss,
            'risk_multiple': risk_multiple,
            'exit_reason': exit_reason,
            'hold_time_hours': hold_time,
            'instrument': ACTIVE_INSTRUMENT
        }
        
        self.trades.append(trade_data)
        
        # Actualizar capital
        self.capital += profit_loss
        
        # Actualizar contador de pérdidas consecutivas
        if profit_loss <= 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Log de salida
        print(f"{self.position_type.upper() if self.position_type else 'UNKNOWN'} EXIT - {exit_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"Exit Price: {exit_price:.1f}")
        print(f"P&L: ${profit_loss:.2f} ({risk_multiple:.1f}R)")
        print(f"Reason: {exit_reason}")
        print(f"Duration: {hold_time:.1f}h")
        print(f"Capital: ${self.capital:.2f}")
        
        # Reset position state
        self.in_position = False
        self.entry_price = 0
        self.stop_loss = 0
        self.position_type = None
        self.position_size = 0
        self.entry_time = None

    def run_backtest(self):
        """Ejecuta el backtest completo"""
        try:
            print("\n" + "="*60)
            print("INICIANDO CFD BACKTEST")
            print("="*60)
            print(f"Instrumento: {self.instrument_config['name']}")
            print(f"Capital inicial: ${CAPITAL_CONFIG['initial_capital']}")
            print(f"Riesgo por trade: ${CAPITAL_CONFIG['risk_per_trade']}")
            
            # Cargar datos
            print("\nCargando datos...")
            df_15m = pd.read_csv(DATA_CONFIG["csv_file_path_15m"])
            df_4h = pd.read_csv(DATA_CONFIG["csv_file_path_4h"])
            
            # Procesar timestamps
            for df, timeframe in [(df_15m, "15M"), (df_4h, "4H")]:
                print(f"Procesando datos {timeframe}: {len(df)} filas")
                
                # Detectar formato de fecha
                if 'timestamp' in df.columns:
                    df['datetime'] = pd.to_datetime(df['timestamp'])
                elif 'date' in df.columns:
                    df['datetime'] = pd.to_datetime(df['date'])
                elif 'Local time' in df.columns:
                    df['datetime'] = pd.to_datetime(df['Local time'], format='%d.%m.%Y %H:%M:%S.%f GMT%z')
                else:
                    raise ValueError(f"Formato de fecha no reconocido en {timeframe}")
                
                df.set_index('datetime', inplace=True)
                df.sort_index(inplace=True)
                
                # Normalizar nombres de columnas
                df.rename(columns={
                    'Open': 'open', 'High': 'high', 'Low': 'low', 
                    'Close': 'close', 'Volume': 'volume'
                }, inplace=True)
            
            # Calcular indicadores
            df_15m = self.calculate_indicators(df_15m)
            df_4h = self.calculate_indicators(df_4h)
            
            # Ejecutar backtest
            print("\nEjecutando backtest...")
            start_idx = max(
                ICHIMOKU_CONFIG["senkou_periods"],
                FILTERS_CONFIG["volume_sma_periods"],
                FILTERS_CONFIG["atr_periods"]
            )
            
            total_bars = len(df_15m)
            progress_interval = max(1, total_bars // 20)
            
            for i in range(start_idx, total_bars):
                if i % progress_interval == 0:
                    progress = (i / total_bars) * 100
                    print(f"Progreso: {progress:.1f}% - Trades: {len(self.trades)} - Capital: ${self.capital:.2f}")
                
                current_time = df_15m.index[i]
                current_price = df_15m['close'].iloc[i]
                
                # Verificar horarios de trading
                if not self.is_trading_hours(current_time):
                    continue
                
                if self.in_position:
                    # Gestionar posición abierta
                    self.manage_open_position(current_price, current_time)
                else:
                    # Buscar nuevas oportunidades
                    self.execute_trade_entry(df_15m, i, df_4h, current_time, current_price)
            
            print("\n" + "="*60)
            print("BACKTEST COMPLETADO")
            print("="*60)
            
            return self.generate_results()
            
        except Exception as e:
            print(f"Error durante el backtest: {str(e)}")
            import traceback
            print(traceback.format_exc())
            raise

    def generate_results(self):
        """Genera y muestra los resultados del backtest"""
        if not self.trades:
            print("No se ejecutaron trades durante el período")
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_profit': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'final_capital': self.capital,
                'df_trades': pd.DataFrame()
            }
        
        # Crear DataFrame de trades
        df_trades = pd.DataFrame(self.trades)
        
        # Calcular métricas
        total_trades = len(df_trades)
        winners = df_trades[df_trades['profit_loss'] > 0]
        losers = df_trades[df_trades['profit_loss'] <= 0]
        win_rate = len(winners) / total_trades * 100
        
        total_profit = df_trades['profit_loss'].sum()
        avg_winner = winners['profit_loss'].mean() if not winners.empty else 0
        avg_loser = losers['profit_loss'].mean() if not losers.empty else 0
        
        gross_profits = winners['profit_loss'].sum() if not winners.empty else 0
        gross_losses = abs(losers['profit_loss'].sum()) if not losers.empty else 0
        profit_factor = gross_profits / gross_losses if gross_losses > 0 else float('inf')
        
        # Calcular drawdown
        df_trades['cumulative_profit'] = df_trades['profit_loss'].cumsum()
        df_trades['capital_curve'] = CAPITAL_CONFIG["initial_capital"] + df_trades['cumulative_profit']
        df_trades['peak'] = df_trades['capital_curve'].cummax()
        df_trades['drawdown'] = (df_trades['peak'] - df_trades['capital_curve']) / df_trades['peak'] * 100
        max_drawdown = df_trades['drawdown'].max()
        
        # Mostrar resultados
        print(f"\n📊 RESULTADOS DEL BACKTEST")
        print(f"{'='*40}")
        print(f"Total de trades: {total_trades}")
        print(f"Trades ganadores: {len(winners)} ({win_rate:.1f}%)")
        print(f"Trades perdedores: {len(losers)}")
        print(f"\n💰 RENTABILIDAD")
        print(f"Beneficio total: ${total_profit:.2f}")
        print(f"Capital final: ${self.capital:.2f}")
        print(f"ROI: {((self.capital / CAPITAL_CONFIG['initial_capital']) - 1) * 100:.1f}%")
        print(f"\n📈 MÉTRICAS")
        print(f"Profit Factor: {profit_factor:.2f}")
        print(f"Avg Winner: ${avg_winner:.2f}")
        print(f"Avg Loser: ${avg_loser:.2f}")
        print(f"Máximo Drawdown: {max_drawdown:.1f}%")
        
        # Guardar resultados
        if LOGGING_CONFIG["save_detailed_report"]:
            self.save_results(df_trades)
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'profit_factor': profit_factor,
            'max_drawdown': max_drawdown,
            'final_capital': self.capital,
            'df_trades': df_trades
        }

    def save_results(self, df_trades):
        """Guarda los resultados en archivos"""
        # Crear directorio si no existe
        os.makedirs(LOGGING_CONFIG["output_directory"], exist_ok=True)
        
        # Guardar trades detallados
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{LOGGING_CONFIG['output_directory']}{LOGGING_CONFIG['file_prefix']}_{ACTIVE_INSTRUMENT}_{timestamp}.csv"
        df_trades.to_csv(filename, index=False)
        print(f"\n💾 Resultados guardados en: {filename}")
        
        # Generar gráfica de equity
        if LOGGING_CONFIG["save_equity_curve"]:
            self.plot_equity_curve(df_trades, timestamp)

    def plot_equity_curve(self, df_trades, timestamp):
        """Genera gráfica de curva de equity"""
        plt.figure(figsize=(15, 10))
        
        # Equity curve
        plt.subplot(2, 1, 1)
        plt.plot(df_trades['exit_time'], df_trades['capital_curve'], 'b-', linewidth=2)
        plt.title(f'Curva de Equity - {self.instrument_config["name"]}')
        plt.ylabel('Capital ($)')
        plt.grid(True, alpha=0.3)
        
        # Drawdown
        plt.subplot(2, 1, 2)
        plt.fill_between(df_trades['exit_time'], df_trades['drawdown'], 0, color='red', alpha=0.3)
        plt.plot(df_trades['exit_time'], df_trades['drawdown'], 'r-')
        plt.title('Drawdown')
        plt.ylabel('Drawdown (%)')
        plt.xlabel('Fecha')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Guardar gráfica
        chart_filename = f"{LOGGING_CONFIG['output_directory']}equity_curve_{ACTIVE_INSTRUMENT}_{timestamp}.png"
        plt.savefig(chart_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"📈 Gráfica guardada en: {chart_filename}")

# Función principal para ejecutar desde script externo
def run_cfd_backtest():
    """Función principal para ejecutar el backtest"""
    print_current_config()
    
    if not validate_config():
        return None
    
    engine = CFDBacktestEngine()
    results = engine.run_backtest()
    
    return results
