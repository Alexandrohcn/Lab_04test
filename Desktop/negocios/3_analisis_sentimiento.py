"""
Script 3 MEJORADO: Análisis de Sentimiento usando Base de Datos CSV
Lee datos desde CSV, analiza sentimiento y guarda resultados en CSV
"""

import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import random

print("=" * 70)
print("ANÁLISIS DE SENTIMIENTO - USANDO BASE DE DATOS CSV")
print("=" * 70)

# ========== 1. GENERAR NOTICIAS Y GUARDAR EN CSV ==========
print("\n[1/3] Generando noticias y guardando en CSV...")

noticias_ejemplos = [
    "OPEP anuncia recorte de producción, precios del petróleo suben",
    "Demanda china de petróleo aumenta por recuperación económica",
    "Inventarios de crudo disminuyen más de lo esperado",
    "Tensiones geopolíticas impulsan precios del petróleo al alza",
    "Inventarios de petróleo aumentan más de lo esperado",
    "Preocupaciones por recesión global presionan precios del crudo",
    "Petroperú anuncia inversión en refinería de Talara",
    "Empresas peruanas se benefician de alza del petróleo",
    "Precio del petróleo se mantiene estable en la sesión",
    "Mercado petrolero espera datos de inventarios semanales"
]

# Generar 100 noticias con fechas
noticias_data = []
for i in range(100):
    fecha = (datetime.now() - pd.Timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d')
    noticia = random.choice(noticias_ejemplos)
    noticias_data.append({
        'noticia_id': f'NOT{i+1:05d}',
        'fecha': fecha,
        'texto': noticia,
        'fuente': random.choice(['Google News', 'Reuters', 'Bloomberg', 'El Comercio'])
    })

df_noticias = pd.DataFrame(noticias_data)
df_noticias.to_csv('base_datos_csv/noticias.csv', index=False)
print(f"  ✓ Noticias guardadas en CSV: {len(df_noticias)} registros")

# ========== 2. ANALIZAR SENTIMIENTO ==========
print("\n[2/3] Analizando sentimiento con VADER...")

analyzer = SentimentIntensityAnalyzer()

sentimientos = []
for idx, row in df_noticias.iterrows():
    scores = analyzer.polarity_scores(row['texto'])
    sentimientos.append({
        'noticia_id': row['noticia_id'],
        'fecha': row['fecha'],
        'texto': row['texto'],
        'score_compound': scores['compound'],
        'score_positivo': scores['pos'],
        'score_neutral': scores['neu'],
        'score_negativo': scores['neg'],
        'clasificacion': 'POSITIVO' if scores['compound'] > 0.05 else 'NEGATIVO' if scores['compound'] < -0.05 else 'NEUTRAL'
    })

df_sentimientos = pd.DataFrame(sentimientos)
df_sentimientos.to_csv('base_datos_csv/sentimientos.csv', index=False)
print(f"  ✓ Sentimientos guardados en CSV: {len(df_sentimientos)} registros")

# ========== 3. INTEGRAR CON PREDICCIÓN ==========
print("\n[3/3] Integrando con predicción desde CSV...")

try:
    # Leer predicción desde CSV
    df_prediccion = pd.read_csv('base_datos_csv/predicciones_prophet.csv')
    df_wti = pd.read_csv('base_datos_csv/petroleo/wti.csv')
    
    precio_actual = df_wti['precio_cierre'].iloc[-1]
    precio_predicho = df_prediccion['precio_predicho'].iloc[-1]
    cambio_precio = ((precio_predicho - precio_actual) / precio_actual) * 100
    
    sentimiento_promedio = df_sentimientos['score_compound'].mean()
    
    # Determinar señal integrada
    if cambio_precio > 0 and sentimiento_promedio > 0.05:
        señal = "FUERTEMENTE BULLISH"
        recomendacion = "COMPRAR"
    elif cambio_precio < 0 and sentimiento_promedio < -0.05:
        señal = "FUERTEMENTE BEARISH"
        recomendacion = "VENDER"
    else:
        señal = "NEUTRAL"
        recomendacion = "MANTENER"
    
    # Guardar señal integrada en CSV
    señal_data = [{
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'precio_actual': precio_actual,
        'precio_predicho': precio_predicho,
        'cambio_porcentual': cambio_precio,
        'sentimiento_promedio': sentimiento_promedio,
        'señal': señal,
        'recomendacion': recomendacion
    }]
    
    df_señal = pd.DataFrame(señal_data)
    df_señal.to_csv('base_datos_csv/señal_mercado.csv', index=False)
    print(f"  ✓ Señal de mercado guardada en CSV")
    
    print("\n" + "=" * 70)
    print("RESULTADOS")
    print("=" * 70)
    
    print(f"\n📊 SENTIMIENTO:")
    print(f"  • Score promedio: {sentimiento_promedio:.3f}")
    print(f"  • Clasificación: {señal}")
    
    print(f"\n🎯 SEÑAL INTEGRADA:")
    print(f"  • Señal: {señal}")
    print(f"  • Recomendación: {recomendacion}")
    
except FileNotFoundError:
    print("  ⚠️ Ejecuta primero: python 2_prediccion_prophet.py")

print("\n✓ Archivos CSV generados:")
print("  • base_datos_csv/noticias.csv")
print("  • base_datos_csv/sentimientos.csv")
print("  • base_datos_csv/señal_mercado.csv")
print("=" * 70)
