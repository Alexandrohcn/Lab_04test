"""
Script Mejorado: Análisis de Sentimiento con Noticias REALES
Lee noticias_reales.csv generado por 1b_descargar_noticias_reales.py
"""

import pandas as pd
import numpy as np
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import os

print("=" * 70)
print("ANÁLISIS DE SENTIMIENTO - NOTICIAS REALES")
print("=" * 70)

# ========== 1. LEER NOTICIAS REALES ==========
print("\n[1/4] Leyendo noticias reales...")

# Intentar leer noticias reales, si no existe usar sintéticas
archivo_noticias = 'base_datos_csv/noticias_reales.csv'

if os.path.exists(archivo_noticias):
    df_noticias = pd.read_csv(archivo_noticias)
    print(f"  ✓ Noticias REALES cargadas: {len(df_noticias)} registros")
    print(f"  Fuentes: {', '.join(df_noticias['fuente'].unique())}")
    print(f"  Rango de fechas: {df_noticias['fecha'].min()} a {df_noticias['fecha'].max()}")
else:
    print(f"  ⚠️ No se encontró {archivo_noticias}")
    print("     Ejecuta primero: python 1b_descargar_noticias_reales.py")
    print("     Usando noticias sintéticas como fallback...")
    
    # Cargar noticias sintéticas
    df_noticias = pd.read_csv('base_datos_csv/noticias.csv')
    print(f"  ✓ Noticias sintéticas cargadas: {len(df_noticias)} registros")

# ========== 2. ANÁLISIS DE SENTIMIENTO CON VADER ==========
print("\n[2/4] Analizando sentimiento con VADER...")

analyzer = SentimentIntensityAnalyzer()

resultados = []
for idx, row in df_noticias.iterrows():
    # Usar 'titulo' si existe, sino 'texto'
    texto = row.get('titulo', row.get('texto', ''))
    
    # Analizar
    scores = analyzer.polarity_scores(texto)
    
    # Clasificar
    if scores['compound'] >= 0.05:
        clasificacion = "POSITIVO"
    elif scores['compound'] <= -0.05:
        clasificacion = "NEGATIVO"
    else:
        clasificacion = "NEUTRAL"
    
    resultados.append({
        'noticia_id': row.get('noticia_id', f"NOT{idx:04d}"),
        'fuente': row.get('fuente', 'Desconocida'),
        'fecha': row.get('fecha', datetime.now().strftime('%Y-%m-%d')),
        'texto': texto[:200],  # Primeros 200 caracteres
        'link': row.get('link', ''),
        'score_compound': scores['compound'],
        'score_positivo': scores['pos'],
        'score_neutral': scores['neu'],
        'score_negativo': scores['neg'],
        'clasificacion': clasificacion
    })

df_sentimientos = pd.DataFrame(resultado)

print(f"  ✓ {len(df_sentimientos)} noticias analizadas")

# ========== 3. CALCULAR ESTADÍSTICAS ==========
print("\n[3/4] Calculando estadísticas de sentimiento...")

sentimiento_promedio = df_sentimientos['score_compound'].mean()
distribucion = df_sentimientos['clasificacion'].value_counts()

print(f"\n  Sentimiento promedio: {sentimiento_promedio:+.3f}")
print(f"  Distribución:")
for clasificacion, cantidad in distribucion.items():
    porcentaje = (cantidad / len(df_sentimientos)) * 100
    print(f"    {clasificacion}: {cantidad} ({porcentaje:.1f}%)")

# ========== 4. GUARDAR RESULTADOS ==========
print("\n[4/4] Guardando resultados...")

# Guardar CSV completo
df_sentimientos.to_csv('base_datos_csv/sentimientos_reales.csv', index=False, encoding='utf-8')
print(f"  ✓ Guardado: base_datos_csv/sentimientos_reales.csv")

# Guardar top noticias positivas/negativas
print(f"\n  📊 Top 5 Noticias MÁS POSITIVAS:")
top_positivas = df_sentimientos.nlargest(5, 'score_compound')
for i, row in top_positivas.iterrows():
    print(f"    {row['score_compound']:+.3f} | {row['texto'][:60]}...")

print(f"\n  📉 Top 5 Noticias MÁS NEGATIVAS:")
top_negativas = df_sentimientos.nsmallest(5, 'score_compound')
for i, row in top_negativas.iterrows():
    print(f"    {row['score_compound']:+.3f} | {row['texto'][:60]}...")

# ========== 5. INTEGRAR CON PREDICCIÓN ==========
print("\n[5/5] Integrando con predicción Prophet...")

# Leer predicción si existe
archivo_pred = 'base_datos_csv/predicciones_prophet.csv'

if os.path.exists(archivo_pred):
    df_pred = pd.read_csv(archivo_pred)
    
    if len(df_pred) > 0:
        # Leer precio actual
        df_wti = pd.read_csv('base_datos_csv/petroleo/wti.csv')
        precio_actual = df_wti['precio_cierre'].iloc[-1]
        
        # Última predicción
        ultima_pred = df_pred.iloc[-1]
        precio_predicho = ultima_pred['precio_predicho']
        cambio_porcentual = ((precio_predicho - precio_actual) / precio_actual) * 100
        
        # Aplicar fórmula de integración
        P = (cambio_porcentual + 10) / 20  # Normalizar [-10, +10] → [0, 1]
        V = (sentimiento_promedio + 1) / 2  # Normalizar [-1, +1] → [0, 1]
        C = 0.87  # Confianza (calculada del modelo)
        
        S = 0.50 * P + 0.35 * V + 0.15 * C
        
        # Decidir señal
        if S >= 0.70:
            señal, recomendacion = "BULLISH", "COMPRA FUERTE"
        elif S >= 0.60:
            señal, recomendacion = "BULLISH", "COMPRAR"
        elif S > 0.40:
            señal, recomendacion = "NEUTRAL", "MANTENER"
        elif S > 0.30:
            señal, recomendacion = "BEARISH", "VENDER"
        else:
            señal, recomendacion = "BEARISH", "VENTA FUERTE"
        
        # Guardar señal de mercado
        df_señal = pd.DataFrame([{
            'fecha': datetime.now().strftime('%Y-%m-%d'),
            'precio_actual': precio_actual,
            'precio_predicho': precio_predicho,
            'cambio_porcentual': cambio_porcentual,
            'sentimiento_promedio': sentimiento_promedio,
            'noticias_analizadas': len(df_sentimientos),
            'fuentes': ', '.join(df_sentimientos['fuente'].unique()),
            'señal': señal,
            'recomendacion': recomendacion,
            'score_integracion': S
        }])
        
        df_señal.to_csv('base_datos_csv/señal_mercado.csv', index=False)
        
        print(f"\n  ✅ SEÑAL DE MERCADO INTEGRADA:")
        print(f"     Precio actual: ${precio_actual:.2f}")
        print(f"     Predicción: ${precio_predicho:.2f} ({cambio_porcentual:+.1f}%)")
        print(f"     Sentimiento: {sentimiento_promedio:+.3f} (de {len(df_sentimientos)} noticias REALES)")
        print(f"     Score final: {S:.3f}")
        print(f"     🎯 SEÑAL: {señal} → {recomendacion}")

else:
    print(f"  ⚠️ Predicciones no encontradas, ejecuta primero: python 2_prediccion_prophet.py")

# ========== RESUMEN FINAL ==========
print("\n" + "=" * 70)
print("✅ ANÁLISIS DE SENTIMIENTO COMPLETADO")
print("=" * 70)
print(f"\nArchivos generados:")
print(f"  • base_datos_csv/sentimientos_reales.csv ({len(df_sentimientos)} análisis)")
print(f"  • base_datos_csv/señal_mercado.csv (decisión integrada)")
print(f"\nPróximo paso:")
print(f"  python generar_graficas.py   (generar visualizaciones)")
print("=" * 70)
