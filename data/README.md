# Data Directory

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
