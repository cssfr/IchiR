# CFD Backtesting System 🚀

Sistema completo de backtesting para CFDs con indicadores Ichimoku, filtros avanzados y optimización de parámetros.

## 📋 Características Principales

- **Multi-timeframe**: Análisis de tendencia en 4H + señales en 15M
- **Gestión de riesgo avanzada**: Position sizing automático + trailing stops
- **Filtros múltiples**: Volumen, ATR, RSI, horarios de trading, distancia de stop
- **Spreads reales**: Simulación de costos de broker con spreads fijos
- **Optimización automática**: Búsqueda de parámetros óptimos
- **Reportes detallados**: Métricas profesionales + gráficas de equity

## 🏗️ Estructura del Proyecto

```
├── config.py                 # 📝 Configuración principal
├── cfd_backtest_engine.py     # 🔧 Motor de backtesting
├── main.py                    # ▶️  Script principal
├── optimize.py                # 🎯 Optimización de parámetros
├── data/                      # 📁 Archivos de datos
│   ├── UK100_15M.csv
│   ├── UK100_4H.csv
│   ├── WallStreet30_15M.csv
│   └── WallStreet30_4H.csv
└── results/                   # 📊 Resultados y reportes
    ├── trades_*.csv
    ├── equity_curve_*.png
    └── optimization_*.csv
```

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8 o superior
- pip (incluido con Python)
- git (opcional, para clonar el repositorio)

### 1. Obtener el Proyecto
```bash
# Opción A: Clonar con git
git clone <repository-url>
cd cfd-backtesting-system

# Opción B: Descargar ZIP y extraer
# Luego navegar al directorio del proyecto
```

### 2. Configuración Inicial Automática
```bash
# Ejecutar script de setup (recomendado)
python setup.py

# Esto creará:
# - Entorno virtual (venv/)
# - Estructura de directorios
# - Archivos README necesarios
```

### 3. Instalación Manual (Alternativa)
```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python check_dependencies.py
```

### 4. Estructura Final del Proyecto
```
cfd-backtesting-system/
├── 📝 config.py                    # Configuración principal
├── 🔧 cfd_backtest_engine.py       # Motor de backtesting  
├── ▶️  main.py                      # Script principal
├── 🎯 optimize.py                   # Optimización de parámetros
├── ⚙️  setup.py                     # Configuración inicial
├── 🔍 check_dependencies.py        # Verificador de dependencias
├── 📋 requirements.txt             # Dependencias de Python
├── 🚫 .gitignore                   # Archivos ignorados por git
├── 📖 README.md                    # Esta documentación
├── 🐍 venv/                        # Entorno virtual (auto-generado)
├── 📊 data/                        # Datos históricos CSV
├── 📈 results/                     # Resultados y reportes
└── 📝 logs/                        # Logs del sistema
```

## ⚡ Inicio Rápido

### 1. Configuración del Entorno
```bash
# IMPORTANTE: Siempre activar el entorno virtual primero
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Verificar que todo está correcto
python check_dependencies.py
```

### 2. Configuración Básica

Edita `config.py` para definir tu configuración:

```python
# Instrumento activo
ACTIVE_INSTRUMENT = "UK100"  # UK100, WallStreet30, Germany40

# Capital y riesgo
CAPITAL_CONFIG = {
    "initial_capital": 1000,
    "risk_per_trade": 10      # $10 por trade
}

# Archivos de datos
DATA_CONFIG = {
    "csv_file_path_15m": "data/UK100_15M.csv",
    "csv_file_path_4h": "data/UK100_4H.csv"
}
```

### 3. Preparar Datos
```bash
# Colocar archivos CSV en data/
# Ver data/README.md para formato requerido
cp tu_archivo_15M.csv data/UK100_15M.csv
cp tu_archivo_4H.csv data/UK100_4H.csv
```

### 4. Ejecutar Backtest

```bash
# Backtest básico
python main.py

# Ver configuración actual
python main.py --config

# Ver ayuda
python main.py --help
```

### 5. Optimizar Parámetros

```bash
# Optimización rápida
python optimize.py

# Seguir las opciones del menú interactivo
```

## 🔧 Gestión del Entorno Virtual

### Comandos Importantes
```bash
# Activar entorno virtual (SIEMPRE antes de trabajar)
# Windows:
venv\Scripts\activate
# Linux/macOS:  
source venv/bin/activate

# Verificar que estás en el entorno virtual
# Deberías ver (venv) al inicio de tu prompt
which python  # Linux/macOS - debe apuntar a venv/bin/python
where python   # Windows - debe apuntar a venv\Scripts\python.exe

# Instalar nueva dependencia
pip install nueva-libreria

# Actualizar requirements.txt si agregaste dependencias
pip freeze > requirements.txt

# Desactivar entorno virtual
deactivate

# Eliminar entorno virtual (si es necesario)
# Windows:
rmdir /s venv
# Linux/macOS:
rm -rf venv
```

## 📊 Instrumentos Soportados

| Instrumento | Spread | Margen | Horarios GMT |
|-------------|---------|---------|--------------|
| UK100 (FTSE) | 1.0 pts | 5% | 08:00-16:30 |
| WallStreet30 (Dow) | 2.0 pts | 5% | 00:00-23:59 |
| Germany40 (DAX) | 1.5 pts | 5% | 08:00-22:00 |

## 🎯 Estrategia de Trading

### Señales de Entrada

**Timeframe Principal (4H)**:
- Determina la tendencia general usando la nube Ichimoku
- Long: Precio por encima de la nube
- Short: Precio por debajo de la nube

**Timeframe de Entrada (15M)**:
- Señal long: Tenkan-sen cruza por encima de Kijun-sen
- Señal short: Tenkan-sen cruza por debajo de Kijun-sen

### Filtros Aplicados

1. **Filtro de Volumen**: Volumen > 1.3x media móvil
2. **Filtro de ATR**: Volatilidad > 1.1x período anterior
3. **Filtro de Horarios**: Solo durante horarios de mercado
4. **Filtro de Distancia Stop**: Entre 15-150 puntos (UK100)
5. **Filtro de Spread**: Máximo 3x el spread normal

### Gestión de Riesgo

- **Position Sizing**: Riesgo fijo por trade ($10)
- **Stop Loss**: Borde de la nube Ichimoku
- **Trailing Stop**: 2% cuando está en ganancia
- **Máximo 3 trades por día**
- **Cooldown de 60 minutos entre trades**

## ⚙️ Configuración Detallada

### Parámetros de Capital
```python
CAPITAL_CONFIG = {
    "initial_capital": 1000,          # Capital inicial
    "risk_per_trade": 10,             # Riesgo por trade
    "max_risk_percentage": 0.02,      # Máximo 2% del capital
    "min_capital_required": 500       # Capital mínimo para continuar
}
```

### Filtros Técnicos
```python
FILTERS_CONFIG = {
    "use_volume_filter": True,
    "use_atr_filter": True,
    "use_trading_hours_filter": True,
    "volume_threshold": 1.3,          # 1.3x la media
    "atr_threshold": 1.1,             # 1.1x el anterior
    "max_spread_multiplier": 3.0      # Máximo 3x spread normal
}
```

### Gestión de Riesgo
```python
RISK_CONFIG = {
    "trailing_stop_percent": 0.02,    # 2% trailing stop
    "max_trades_per_day": 3,          # Máximo trades/día
    "cooldown_minutes": 60,           # Cooldown entre trades
    "max_consecutive_losses": 5       # Parar tras 5 pérdidas seguidas
}
```

## 📈 Cálculo de Position Size

El sistema calcula automáticamente el tamaño de posición:

```python
# Ejemplo para UK100
entry_price = 7850.0
stop_loss = 7800.0
risk_per_trade = 10.0
unit_value = 0.50

# Cálculo
risk_distance = 50.0 puntos
risk_per_unit = 50.0 × 0.50 = $25.00
position_size = $10.00 ÷ $25.00 = 0.4 → 0.5 unidades (redondeado)
```

## 📊 Métricas de Evaluación

- **Win Rate**: Porcentaje de trades ganadores
- **Profit Factor**: Ganancias brutas ÷ Pérdidas brutas
- **Sharpe Ratio**: Retorno ajustado por riesgo
- **Maximum Drawdown**: Mayor caída desde el pico
- **Average R**: Múltiplos de riesgo promedio

## 🔧 Optimización

### Parámetros Optimizables

1. **Volume Threshold**: 1.0 - 2.5 (paso 0.2)
2. **ATR Threshold**: 0.8 - 1.8 (paso 0.2)
3. **Trailing Stop**: 1% - 5% (paso 0.5%)

### Métricas de Optimización

- `profit_factor`: Rentabilidad relativa (recomendado)
- `total_profit`: Beneficio absoluto
- `win_rate`: Tasa de acierto
- `sharpe_ratio`: Retorno ajustado por riesgo

### Ejemplo de Optimización

```bash
python optimize.py
# Elegir opción 1 (optimización rápida)
# Resultados automáticamente guardados en results/
```

## 📁 Formato de Datos

Los archivos CSV deben tener estas columnas:

```csv
Local time,Open,High,Low,Close,Volume
01.01.2022 00:00:00.000 GMT+0,7850.5,7855.0,7848.0,7852.5,1250
```

O alternativamente:
```csv
timestamp,open,high,low,close,volume
```

## 🚨 Consideraciones Importantes

### Limitaciones
- ⚠️ Los resultados son simulaciones y no garantizan rendimientos futuros
- ⚠️ No incluye slippage variable ni problemas de ejecución
- ⚠️ Los spreads son fijos y pueden variar en mercados reales

### Buenas Prácticas
- ✅ Usar al menos 1000 barras de datos históricos
- ✅ Validar resultados en períodos separados (out-of-sample)
- ✅ Mantener riesgo por trade < 2% del capital
- ✅ Considerar costos de financiamiento overnight

### Validación de Estrategia
- 📊 Mínimo 30 trades para considerar estadísticamente significativo
- 📊 Profit Factor > 1.3 para robustez
- 📊 Maximum Drawdown < 20% para viabilidad
- 📊 Win Rate > 40% para consistencia

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para detalles.

## 🔗 Enlaces Útiles

- [Documentación de TA-Lib](https://mrjbq7.github.io/ta-lib/)
- [Ichimoku Strategy Guide](https://www.investopedia.com/terms/i/ichimoku-cloud.asp)
- [CFD Trading Basics](https://www.investopedia.com/terms/c/contractfordifferences.asp)

## ⚡ Soporte

Para preguntas o problemas:
- Crear un Issue en GitHub
- Revisar la documentación en `config.py`
- Verificar logs de error en el directorio `results/`

---

**⚠️ Disclaimer**: Este software es solo para fines educativos y de backtesting. No constituye asesoramiento financiero. Siempre realiza tu propia investigación antes de invertir dinero real.