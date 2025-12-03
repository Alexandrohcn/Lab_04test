"""
Script 1 MEJORADO: Descargar Datos y Crear Base de Datos CSV
Descarga datos del petróleo, empresas peruanas y crea estructura de BD en CSV
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import os
import requests

# Crear estructura de base de datos
os.makedirs('base_datos_csv', exist_ok=True)
os.makedirs('base_datos_csv/petroleo', exist_ok=True)
os.makedirs('base_datos_csv/empresas_usa', exist_ok=True)
os.makedirs('base_datos_csv/empresas_peru', exist_ok=True)
os.makedirs('base_datos_csv/economicos', exist_ok=True)

print("=" * 70)
print("CREACIÓN DE BASE DE DATOS CSV - SISTEMA DE ANÁLISIS DE PETRÓLEO")
print("=" * 70)

# Fechas
end_date = datetime.now()
start_date = end_date - timedelta(days=5*365)

# ========== 1. TABLA: PETROLEO ==========
print("\n[1/5] Creando tabla PETROLEO...")

# WTI
# WTI
print("  → Descargando WTI...")
wti = yf.download('CL=F', start=start_date, end=end_date, progress=False)

# Flatten MultiIndex columns if present
if isinstance(wti.columns, pd.MultiIndex):
    wti.columns = wti.columns.get_level_values(0)

wti_df = pd.DataFrame({
    'fecha': wti.index,
    'tipo': 'WTI',
    'precio_apertura': wti['Open'].values.flatten(),
    'precio_cierre': wti['Close'].values.flatten(),
    'precio_maximo': wti['High'].values.flatten(),
    'precio_minimo': wti['Low'].values.flatten(),
    'volumen': wti['Volume'].values.flatten()
})
wti_df.to_csv('base_datos_csv/petroleo/wti.csv', index=False)
print(f"  ✓ Tabla WTI: {len(wti_df)} registros")

# Brent
print("  → Descargando Brent...")
brent = yf.download('BZ=F', start=start_date, end=end_date, progress=False)

if isinstance(brent.columns, pd.MultiIndex):
    brent.columns = brent.columns.get_level_values(0)

brent_df = pd.DataFrame({
    'fecha': brent.index,
    'tipo': 'Brent',
    'precio_apertura': brent['Open'].values.flatten(),
    'precio_cierre': brent['Close'].values.flatten(),
    'precio_maximo': brent['High'].values.flatten(),
    'precio_minimo': brent['Low'].values.flatten(),
    'volumen': brent['Volume'].values.flatten()
})
brent_df.to_csv('base_datos_csv/petroleo/brent.csv', index=False)
print(f"  ✓ Tabla Brent: {len(brent_df)} registros")

# ========== 2. TABLA: EMPRESAS_USA ==========
print("\n[2/5] Creando tabla EMPRESAS_USA (petroleras)...")

empresas_usa = {
    'XOM': {'nombre': 'ExxonMobil', 'sector': 'Petrolera', 'pais': 'USA'},
    'CVX': {'nombre': 'Chevron', 'sector': 'Petrolera', 'pais': 'USA'},
    'OXY': {'nombre': 'Occidental Petroleum', 'sector': 'Petrolera', 'pais': 'USA'},
    'SLB': {'nombre': 'Schlumberger', 'sector': 'Servicios Petroleros', 'pais': 'USA'},
    'HAL': {'nombre': 'Halliburton', 'sector': 'Servicios Petroleros', 'pais': 'USA'},
    'VLO': {'nombre': 'Valero Energy', 'sector': 'Refinería', 'pais': 'USA'},
    'DAL': {'nombre': 'Delta Airlines', 'sector': 'Aerolínea', 'pais': 'USA'},
    'UAL': {'nombre': 'United Airlines', 'sector': 'Aerolínea', 'pais': 'USA'},
    'FDX': {'nombre': 'FedEx', 'sector': 'Transporte', 'pais': 'USA'}
}

# Catálogo de empresas
catalogo_usa = []
for ticker, info in empresas_usa.items():
    catalogo_usa.append({
        'ticker': ticker,
        'nombre': info['nombre'],
        'sector': info['sector'],
        'pais': info['pais']
    })

df_catalogo_usa = pd.DataFrame(catalogo_usa)
df_catalogo_usa.to_csv('base_datos_csv/empresas_usa/catalogo.csv', index=False)
print(f"  ✓ Catálogo USA: {len(df_catalogo_usa)} empresas")

# Precios históricos de cada empresa
for ticker, info in empresas_usa.items():
    print(f"  → Descargando {ticker} ({info['nombre']})...")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df_empresa = pd.DataFrame({
            'fecha': data.index,
            'ticker': ticker,
            'precio_apertura': data['Open'].values.flatten(),
            'precio_cierre': data['Close'].values.flatten(),
            'precio_maximo': data['High'].values.flatten(),
            'precio_minimo': data['Low'].values.flatten(),
            'volumen': data['Volume'].values.flatten()
        })
        df_empresa.to_csv(f'base_datos_csv/empresas_usa/{ticker}.csv', index=False)
        print(f"  ✓ {ticker}: {len(df_empresa)} registros")
    except Exception as e:
        print(f"  ✗ Error en {ticker}: {e}")

# ========== 3. TABLA: EMPRESAS_PERU (BVL) ==========
print("\n[3/5] Creando tabla EMPRESAS_PERU (Bolsa de Lima)...")

# Empresas peruanas relacionadas con energía/petróleo
empresas_peru = {
    'PETRO1.LM': {'nombre': 'Petroperú', 'sector': 'Petrolera', 'pais': 'Perú'},
    'SCCO': {'nombre': 'Southern Copper', 'sector': 'Minería', 'pais': 'Perú'},
    'BVN': {'nombre': 'Buenaventura', 'sector': 'Minería', 'pais': 'Perú'},
    'CVERDEC1.LM': {'nombre': 'Casa Verde', 'sector': 'Construcción', 'pais': 'Perú'}
}

# Catálogo de empresas peruanas
catalogo_peru = []
for ticker, info in empresas_peru.items():
    catalogo_peru.append({
        'ticker': ticker,
        'nombre': info['nombre'],
        'sector': info['sector'],
        'pais': info['pais']
    })

df_catalogo_peru = pd.DataFrame(catalogo_peru)
df_catalogo_peru.to_csv('base_datos_csv/empresas_peru/catalogo.csv', index=False)
print(f"  ✓ Catálogo Perú: {len(df_catalogo_peru)} empresas")

# Intentar descargar datos de empresas peruanas
for ticker, info in empresas_peru.items():
    print(f"  → Descargando {ticker} ({info['nombre']})...")
    try:
        data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        if len(data) > 0:
            df_empresa = pd.DataFrame({
                'fecha': data.index,
                'ticker': ticker,
                'precio_apertura': data['Open'].values.flatten(),
                'precio_cierre': data['Close'].values.flatten(),
                'precio_maximo': data['High'].values.flatten(),
                'precio_minimo': data['Low'].values.flatten(),
                'volumen': data['Volume'].values.flatten()
            })
            df_empresa.to_csv(f'base_datos_csv/empresas_peru/{ticker.replace(".", "_")}.csv', index=False)
            print(f"  ✓ {ticker}: {len(df_empresa)} registros")
        else:
            print(f"  ⚠️ {ticker}: Sin datos disponibles, generando sintéticos...")
            # Generar datos sintéticos para demostración
            import numpy as np
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            precio_base = 100 + np.random.randn() * 20
            precios = precio_base + np.cumsum(np.random.randn(len(dates)) * 2)
            
            df_sintetico = pd.DataFrame({
                'fecha': dates,
                'ticker': ticker,
                'precio_apertura': precios + np.random.randn(len(dates)) * 0.5,
                'precio_cierre': precios,
                'precio_maximo': precios + np.abs(np.random.randn(len(dates)) * 1),
                'precio_minimo': precios - np.abs(np.random.randn(len(dates)) * 1),
                'volumen': np.random.randint(10000, 100000, len(dates))
            })
            df_sintetico.to_csv(f'base_datos_csv/empresas_peru/{ticker.replace(".", "_")}.csv', index=False)
            print(f"  ✓ {ticker}: {len(df_sintetico)} registros (sintéticos)")
    except Exception as e:
        print(f"  ✗ Error en {ticker}: {e}")

# ========== 4. TABLA: TIPO_CAMBIO ==========
print("\n[4/5] Creando tabla TIPO_CAMBIO (USD/PEN)...")

try:
    usdpen = yf.download('PEN=X', start=start_date, end=end_date, progress=False)
    
    if isinstance(usdpen.columns, pd.MultiIndex):
        usdpen.columns = usdpen.columns.get_level_values(0)
        
    if len(usdpen) > 0:
        df_tc = pd.DataFrame({
            'fecha': usdpen.index,
            'moneda_origen': 'USD',
            'moneda_destino': 'PEN',
            'tipo_cambio': usdpen['Close'].values.flatten()
        })
    else:
        raise ValueError("Sin datos")
except:
    print("  ⚠️ Generando datos sintéticos de tipo de cambio...")
    import numpy as np
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    tc_base = 3.75
    tc_values = tc_base + np.cumsum(np.random.randn(len(dates)) * 0.01)
    
    df_tc = pd.DataFrame({
        'fecha': dates,
        'moneda_origen': 'USD',
        'moneda_destino': 'PEN',
        'tipo_cambio': tc_values
    })

df_tc.to_csv('base_datos_csv/economicos/tipo_cambio_usdpen.csv', index=False)
print(f"  ✓ Tipo de cambio: {len(df_tc)} registros")

# ========== 5. TABLA: CLIENTES (SIMULADOS) ==========
print("\n[5/5] Creando tabla CLIENTES (datos simulados)...")

import numpy as np

# Generar 1000 clientes peruanos
num_clientes = 1000

nombres = ['Juan', 'María', 'Carlos', 'Ana', 'Luis', 'Rosa', 'Pedro', 'Carmen', 'José', 'Laura']
apellidos = ['García', 'Rodríguez', 'Martínez', 'López', 'Pérez', 'González', 'Sánchez', 'Ramírez', 'Torres', 'Flores']
ciudades = ['Lima', 'Arequipa', 'Cusco', 'Trujillo', 'Chiclayo', 'Piura', 'Iquitos', 'Huancayo', 'Tacna', 'Puno']

clientes = []
for i in range(num_clientes):
    cliente = {
        'cliente_id': f'CLI{i+1:05d}',
        'nombre': np.random.choice(nombres),
        'apellido': np.random.choice(apellidos),
        'ciudad': np.random.choice(ciudades),
        'edad': np.random.randint(25, 65),
        'tipo_inversor': np.random.choice(['Conservador', 'Moderado', 'Agresivo']),
        'capital_inicial': np.random.randint(10000, 500000),
        'fecha_registro': (start_date + timedelta(days=np.random.randint(0, 1800))).strftime('%Y-%m-%d')
    }
    clientes.append(cliente)

df_clientes = pd.DataFrame(clientes)
df_clientes.to_csv('base_datos_csv/clientes.csv', index=False)
print(f"  ✓ Clientes: {len(df_clientes)} registros")

# ========== RESUMEN DE BASE DE DATOS ==========
print("\n" + "=" * 70)
print("ESTRUCTURA DE BASE DE DATOS CSV CREADA")
print("=" * 70)

print("\n📁 Estructura de carpetas:")
print("  base_datos_csv/")
print("  ├── petroleo/")
print("  │   ├── wti.csv")
print("  │   └── brent.csv")
print("  ├── empresas_usa/")
print("  │   ├── catalogo.csv")
print("  │   ├── XOM.csv, CVX.csv, OXY.csv, ...")
print("  ├── empresas_peru/")
print("  │   ├── catalogo.csv")
print("  │   ├── SCCO.csv, BVN.csv, ...")
print("  ├── economicos/")
print("  │   └── tipo_cambio_usdpen.csv")
print("  └── clientes.csv")

print("\n📊 Resumen de tablas:")

# Contar archivos
import glob
total_archivos = len(glob.glob('base_datos_csv/**/*.csv', recursive=True))
total_size = sum(os.path.getsize(f) for f in glob.glob('base_datos_csv/**/*.csv', recursive=True))

print(f"  • Total de archivos CSV: {total_archivos}")
print(f"  • Tamaño total: {total_size / (1024*1024):.2f} MB")

print("\n📋 Tablas principales:")
print(f"  • petroleo/wti.csv: {len(wti_df)} registros")
print(f"  • petroleo/brent.csv: {len(brent_df)} registros")
print(f"  • empresas_usa/: {len(empresas_usa)} empresas")
print(f"  • empresas_peru/: {len(empresas_peru)} empresas")
print(f"  • economicos/tipo_cambio: {len(df_tc)} registros")
print(f"  • clientes.csv: {len(df_clientes)} clientes")

print("\n✓ Base de datos CSV lista para usar!")
print("=" * 70)

# Mostrar preview de clientes peruanos
print("\n👥 PREVIEW: Primeros 10 clientes peruanos")
print(df_clientes.head(10).to_string(index=False))
