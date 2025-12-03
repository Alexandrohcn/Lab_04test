"""
Script 2 MEJORADO: Predicción con Prophet usando Base de Datos CSV
Lee datos desde archivos CSV y genera predicciones
"""

import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("PREDICCIÓN CON PROPHET - USANDO BASE DE DATOS CSV")
print("=" * 70)

# ========== 1. LEER DATOS DESDE CSV ==========
print("\n[1/4] Leyendo datos desde base de datos CSV...")

# Leer WTI desde CSV
df_wti = pd.read_csv('base_datos_csv/petroleo/wti.csv')
print(f"  ✓ WTI cargado: {len(df_wti)} registros")
print(f"  • Rango: {df_wti['fecha'].min()} a {df_wti['fecha'].max()}")

# Leer Brent desde CSV
df_brent = pd.read_csv('base_datos_csv/petroleo/brent.csv')
print(f"  ✓ Brent cargado: {len(df_brent)} registros")

# ========== 2. PREPARAR DATOS PARA PROPHET ==========
print("\n[2/4] Preparando datos para Prophet...")

# Prophet requiere 'ds' (fecha) y 'y' (valor)
df_prophet = pd.DataFrame({
    'ds': pd.to_datetime(df_wti['fecha']),
    'y': df_wti['precio_cierre']
})

df_prophet = df_prophet.dropna()
print(f"  ✓ Datos preparados: {len(df_prophet)} registros")

# ========== 3. ENTRENAR MODELO ==========
print("\n[3/4] Entrenando modelo Prophet...")

model = Prophet(
    daily_seasonality=True,
    weekly_seasonality=True,
    yearly_seasonality=True,
    changepoint_prior_scale=0.05
)

model.fit(df_prophet)
print("  ✓ Modelo entrenado")

# ========== 4. GENERAR PREDICCIONES ==========
print("\n[4/4] Generando predicciones...")

future = model.make_future_dataframe(periods=30, freq='D')
forecast = model.predict(future)

# GUARDAR PREDICCIONES EN CSV
predicciones_csv = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
predicciones_csv.columns = ['fecha', 'precio_predicho', 'limite_inferior', 'limite_superior']
predicciones_csv.to_csv('base_datos_csv/predicciones_prophet.csv', index=False)
print(f"  ✓ Predicciones guardadas en CSV: {len(predicciones_csv)} registros")

# ========== RESULTADOS ==========
print("\n" + "=" * 70)
print("RESULTADOS DE LA PREDICCIÓN")
print("=" * 70)

precio_actual = df_prophet['y'].iloc[-1]
predicciones_futuras = forecast[forecast['ds'] > df_prophet['ds'].max()].head(10)
precio_futuro = predicciones_futuras['yhat'].iloc[-1]
cambio = ((precio_futuro - precio_actual) / precio_actual) * 100

print(f"\n📊 PREDICCIÓN:")
print(f"  • Precio actual WTI: ${precio_actual:.2f}")
print(f"  • Precio en 10 días: ${precio_futuro:.2f}")
print(f"  • Cambio esperado: {cambio:+.2f}%")
print(f"  • Señal: {'ALCISTA ↗️' if cambio > 0 else 'BAJISTA ↘️' if cambio < 0 else 'NEUTRAL →'}")

print("\n🔮 Próximos 5 días:")
for idx, row in predicciones_futuras.head(5).iterrows():
    print(f"  {row['ds'].strftime('%Y-%m-%d')}: ${row['yhat']:.2f} (±${(row['yhat_upper']-row['yhat_lower'])/2:.2f})")

print("\n✓ Predicciones guardadas en: base_datos_csv/predicciones_prophet.csv")
print("=" * 70)
