# config.py - Configuración para CFD Backtesting System

# =============================================================================
# CONFIGURACIÓN DE ARCHIVOS DE DATOS
# =============================================================================

DATA_CONFIG = {
    "csv_file_path_15m": "data/UK100_15M_2022-2025.csv",
    "csv_file_path_4h": "data/UK100_4H_2022-2025.csv"
}

# =============================================================================
# CONFIGURACIÓN DE CAPITAL Y RIESGO
# =============================================================================

CAPITAL_CONFIG = {
    "initial_capital": 1000,          # Capital inicial en USD
    "risk_per_trade": 10,             # Riesgo máximo por operación en USD
    "max_risk_percentage": 0.02,      # Máximo 2% del capital por trade
    "min_capital_required": 500       # Capital mínimo para continuar trading
}

# =============================================================================
# CONFIGURACIÓN DE INSTRUMENTOS CFD
# =============================================================================

INSTRUMENTS = {
    "UK100": {
        "name": "UK100 (FTSE 100)",
        "unit_value": 0.50,                    # USD por punto
        "tick_size": 0.5,                      # Movimiento mínimo del precio
        "min_position_size": 0.5,              # Tamaño mínimo de posición
        "margin_requirement": 0.05,            # 5% de margen (leverage 20:1)
        "spread": 1.0,                         # Spread fijo en puntos
        "trading_hours": {
            "start_hour": 8,                   # 08:00 GMT
            "start_minute": 0,
            "end_hour": 16,                    # 16:30 GMT
            "end_minute": 30
        },
        "stop_limits": {
            "min_stop_distance": 15,           # Mínimo 15 puntos al stop
            "max_stop_distance": 150           # Máximo 150 puntos al stop
        }
    },
    
    "WallStreet30": {
        "name": "WallStreet30 (Dow Jones)",
        "unit_value": 0.50,                    # USD por punto
        "tick_size": 1.0,                      # Movimiento mínimo del precio
        "min_position_size": 0.5,              # Tamaño mínimo de posición
        "margin_requirement": 0.05,            # 5% de margen (leverage 20:1)
        "spread": 2.0,                         # Spread fijo en puntos
        "trading_hours": {
            "start_hour": 0,                   # 00:00 GMT lunes
            "start_minute": 0,
            "end_hour": 23,                    # 23:59 GMT viernes
            "end_minute": 59
        },
        "stop_limits": {
            "min_stop_distance": 25,           # Mínimo 25 puntos al stop
            "max_stop_distance": 300           # Máximo 300 puntos al stop
        }
    },
    
    "Germany40": {
        "name": "Germany40 (DAX)",
        "unit_value": 0.50,                    # USD por punto
        "tick_size": 0.5,                      # Movimiento mínimo del precio
        "min_position_size": 0.5,              # Tamaño mínimo de posición
        "margin_requirement": 0.05,            # 5% de margen (leverage 20:1)
        "spread": 1.5,                         # Spread fijo en puntos
        "trading_hours": {
            "start_hour": 8,                   # 08:00 GMT
            "start_minute": 0,
            "end_hour": 22,                    # 22:00 GMT
            "end_minute": 0
        },
        "stop_limits": {
            "min_stop_distance": 20,           # Mínimo 20 puntos al stop
            "max_stop_distance": 200           # Máximo 200 puntos al stop
        }
    }
}

# Instrumento activo para el backtest
ACTIVE_INSTRUMENT = "UK100"

# =============================================================================
# CONFIGURACIÓN DE GESTIÓN DE RIESGO
# =============================================================================

RISK_CONFIG = {
    "trailing_stop_percent": 0.02,            # Trailing stop del 2%
    "use_trailing_stop": True,                # Activar trailing stop
    "use_fixed_take_profit": False,           # No usar take profit fijo
    "take_profit_ratio": 2.0,                 # Ratio risk/reward si se activa TP
    "max_trades_per_day": 3,                  # Máximo 3 trades por día
    "cooldown_minutes": 60,                   # 60 min entre trades en la misma dirección
    "max_consecutive_losses": 5               # Parar después de 5 pérdidas seguidas
}

# =============================================================================
# CONFIGURACIÓN DE FILTROS TÉCNICOS
# =============================================================================

FILTERS_CONFIG = {
    # Activación de filtros
    "use_volume_filter": True,
    "use_rsi_filter": False,                  # Desactivado para índices
    "use_atr_filter": True,
    "use_spread_filter": True,                # Nuevo: filtro de spread
    "use_trading_hours_filter": True,         # Nuevo: filtro de horarios
    "use_stop_distance_filter": True,         # Nuevo: filtro de distancia stop
    
    # Umbrales de filtros
    "volume_threshold": 1.3,                  # Volumen 1.3x la media móvil
    "atr_threshold": 1.1,                     # ATR 1.1x el anterior
    "rsi_oversold": 30,                       # RSI sobreventa
    "rsi_overbought": 70,                     # RSI sobrecompra
    "max_spread_multiplier": 3.0,             # Máximo 3x el spread normal
    
    # Configuración de medias móviles para filtros
    "volume_sma_periods": 20,                 # SMA de volumen
    "atr_periods": 14,                        # Períodos para ATR
    "rsi_periods": 14                         # Períodos para RSI
}

# =============================================================================
# CONFIGURACIÓN DE INDICADORES ICHIMOKU
# =============================================================================

ICHIMOKU_CONFIG = {
    "tenkan_periods": 9,                      # Tenkan-sen (línea de conversión)
    "kijun_periods": 26,                      # Kijun-sen (línea base)
    "senkou_periods": 52,                     # Senkou Span (nube)
    "displacement": 26                        # Desplazamiento de la nube
}

# =============================================================================
# CONFIGURACIÓN DE TIMEFRAMES
# =============================================================================

TIMEFRAME_CONFIG = {
    "entry_timeframe": "15M",                 # Timeframe para señales de entrada
    "trend_timeframe": "4H",                  # Timeframe para filtro de tendencia
    "min_bars_required": 60,                  # Mínimo de barras para comenzar
    "lookback_periods": 100                   # Períodos hacia atrás para análisis
}

# =============================================================================
# CONFIGURACIÓN DE OPTIMIZACIÓN
# =============================================================================

OPTIMIZATION_CONFIG = {
    "enable_optimization": False,
    "optimization_metric": "profit_factor",   # "profit_factor", "sharpe_ratio", "win_rate"
    "parameter_ranges": {
        "volume_threshold": (1.0, 2.5, 0.2),
        "atr_threshold": (0.8, 1.8, 0.2),
        "trailing_stop": (0.01, 0.05, 0.005)
    },
    "min_trades_for_valid_result": 10,        # Mínimo trades para considerar válido
    "cross_validation_splits": 3              # Splits para validación cruzada
}

# =============================================================================
# CONFIGURACIÓN DE LOGGING Y REPORTES
# =============================================================================

LOGGING_CONFIG = {
    "log_level": "INFO",                      # DEBUG, INFO, WARNING, ERROR
    "log_trades": True,                       # Registrar cada trade
    "log_signals": False,                     # Registrar señales no ejecutadas
    "save_detailed_report": True,             # Guardar reporte detallado
    "save_equity_curve": True,                # Guardar gráfica de equity
    "output_directory": "results/",           # Directorio de resultados
    "file_prefix": "cfd_backtest"             # Prefijo para archivos de salida
}

# =============================================================================
# CONFIGURACIÓN DE VALIDACIÓN
# =============================================================================

VALIDATION_CONFIG = {
    "validate_data_integrity": True,          # Validar integridad de datos
    "remove_outliers": True,                  # Remover outliers de precio
    "outlier_std_threshold": 5,               # Threshold para outliers (desv. std)
    "validate_trading_hours": True,           # Validar horarios en datos
    "min_data_points": 1000,                 # Mínimo de puntos de datos
    "check_data_gaps": True                   # Verificar gaps en datos
}

# =============================================================================
# CONFIGURACIÓN DE DESARROLLO Y DEBUG
# =============================================================================

DEBUG_CONFIG = {
    "debug_mode": False,                      # Modo debug activado
    "verbose_output": False,                  # Output detallado
    "save_intermediate_results": False,       # Guardar resultados intermedios
    "plot_signals": False,                    # Plotear señales en gráficos
    "max_trades_to_log": 100,                # Máximo trades a loggear en detalle
    "progress_update_frequency": 0.1          # Frecuencia de updates (0.1 = 10%)
}

# =============================================================================
# FUNCIONES DE VALIDACIÓN DE CONFIGURACIÓN
# =============================================================================

def validate_config():
    """Valida que la configuración sea coherente"""
    errors = []
    
    # Validar que el instrumento activo existe
    if ACTIVE_INSTRUMENT not in INSTRUMENTS:
        errors.append(f"Instrumento '{ACTIVE_INSTRUMENT}' no está definido en INSTRUMENTS")
    
    # Validar capital y riesgo
    if CAPITAL_CONFIG["risk_per_trade"] > CAPITAL_CONFIG["initial_capital"] * CAPITAL_CONFIG["max_risk_percentage"]:
        errors.append(f"Risk per trade ({CAPITAL_CONFIG['risk_per_trade']}) excede el máximo permitido")
    
    # Validar horarios de trading
    instrument = INSTRUMENTS[ACTIVE_INSTRUMENT]
    hours = instrument["trading_hours"]
    if hours["start_hour"] >= hours["end_hour"]:
        if not (hours["start_hour"] == 23 and hours["end_hour"] < 23):  # Caso especial para mercados 24h
            errors.append(f"Horarios de trading inválidos para {ACTIVE_INSTRUMENT}")
    
    # Validar parámetros de stop
    stops = instrument["stop_limits"]
    if stops["min_stop_distance"] >= stops["max_stop_distance"]:
        errors.append(f"min_stop_distance debe ser menor que max_stop_distance para {ACTIVE_INSTRUMENT}")
    
    # Validar configuración de Ichimoku
    ichimoku = ICHIMOKU_CONFIG
    if ichimoku["tenkan_periods"] >= ichimoku["kijun_periods"]:
        errors.append("tenkan_periods debe ser menor que kijun_periods")
    
    if errors:
        print("ERRORES EN CONFIGURACIÓN:")
        for error in errors:
            print(f"- {error}")
        return False
    
    print("✅ Configuración validada correctamente")
    return True

def get_active_instrument_config():
    """Retorna la configuración del instrumento activo"""
    return INSTRUMENTS[ACTIVE_INSTRUMENT]

def print_current_config():
    """Imprime la configuración actual de manera legible"""
    print("=" * 60)
    print("CONFIGURACIÓN ACTUAL DEL BACKTEST")
    print("=" * 60)
    
    # Instrumento activo
    instrument = get_active_instrument_config()
    print(f"\n📊 INSTRUMENTO: {instrument['name']}")
    print(f"   Valor por unidad: ${instrument['unit_value']}")
    print(f"   Spread fijo: {instrument['spread']} puntos")
    print(f"   Margen requerido: {instrument['margin_requirement']*100}%")
    
    # Capital y riesgo
    print(f"\n💰 CAPITAL Y RIESGO:")
    print(f"   Capital inicial: ${CAPITAL_CONFIG['initial_capital']}")
    print(f"   Riesgo por trade: ${CAPITAL_CONFIG['risk_per_trade']}")
    print(f"   Trailing stop: {RISK_CONFIG['trailing_stop_percent']*100}%")
    
    # Filtros activos
    print(f"\n🎯 FILTROS ACTIVOS:")
    for key, value in FILTERS_CONFIG.items():
        if key.startswith('use_') and value:
            filter_name = key.replace('use_', '').replace('_', ' ').title()
            print(f"   ✅ {filter_name}")
    
    # Horarios
    hours = instrument["trading_hours"]
    print(f"\n⏰ HORARIOS DE TRADING:")
    print(f"   {hours['start_hour']:02d}:{hours['start_minute']:02d} - {hours['end_hour']:02d}:{hours['end_minute']:02d} GMT")
    
    print("=" * 60)

# Ejecutar validación al importar
if __name__ == "__main__":
    print_current_config()
    validate_config()
else:
    # Validar silenciosamente al importar
    validate_config()