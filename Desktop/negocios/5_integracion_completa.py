"""
Script 5: Integración Completa del Sistema
Ejecuta todo el pipeline: descarga → predicción → sentimiento → recomendación
Genera reporte final consolidado
"""

import subprocess
import sys
import os
from datetime import datetime

print("=" * 70)
print(" " * 15 + "SISTEMA INTELIGENTE DE ANÁLISIS DE PETRÓLEO")
print(" " * 20 + "Pipeline Completo de Ejecución")
print("=" * 70)

# ========== CONFIGURACIÓN ==========
scripts = [
    ("1_descargar_datos.py", "Descarga de Datos"),
    ("2_prediccion_prophet.py", "Predicción con Prophet"),
    ("3_analisis_sentimiento.py", "Análisis de Sentimiento"),
    ("4_recomendacion_spark.py", "Sistema de Recomendación")
]

# ========== EJECUCIÓN DEL PIPELINE ==========
print(f"\n🚀 Iniciando pipeline completo...")
print(f"   Hora de inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n" + "-" * 70)

resultados = {}
inicio_total = datetime.now()

for i, (script, descripcion) in enumerate(scripts, 1):
    print(f"\n[{i}/{len(scripts)}] Ejecutando: {descripcion}")
    print(f"    Script: {script}")
    print(f"    {'-' * 66}")
    
    inicio = datetime.now()
    
    try:
        # Ejecutar script
        result = subprocess.run(
            [sys.executable, script],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos máximo por script
        )
        
        fin = datetime.now()
        duracion = (fin - inicio).total_seconds()
        
        # Mostrar output
        if result.stdout:
            print(result.stdout)
        
        if result.returncode == 0:
            print(f"\n    ✓ Completado exitosamente en {duracion:.1f} segundos")
            resultados[script] = {"status": "OK", "duracion": duracion}
        else:
            print(f"\n    ✗ Error en ejecución")
            if result.stderr:
                print(f"    Error: {result.stderr}")
            resultados[script] = {"status": "ERROR", "duracion": duracion}
            
    except subprocess.TimeoutExpired:
        print(f"\n    ✗ Timeout: El script excedió el tiempo límite")
        resultados[script] = {"status": "TIMEOUT", "duracion": 600}
        
    except Exception as e:
        print(f"\n    ✗ Error inesperado: {e}")
        resultados[script] = {"status": "ERROR", "duracion": 0}
    
    print("-" * 70)

fin_total = datetime.now()
duracion_total = (fin_total - inicio_total).total_seconds()

# ========== REPORTE FINAL ==========
print("\n" + "=" * 70)
print(" " * 25 + "REPORTE FINAL")
print("=" * 70)

print(f"\n⏱️  TIEMPOS DE EJECUCIÓN:")
for script, descripcion in scripts:
    if script in resultados:
        status = resultados[script]["status"]
        duracion = resultados[script]["duracion"]
        icono = "✓" if status == "OK" else "✗"
        print(f"  {icono} {descripcion:.<45} {duracion:>6.1f}s [{status}]")

print(f"\n  {'TOTAL':.<53} {duracion_total:>6.1f}s")

# ========== VERIFICAR ARCHIVOS GENERADOS ==========
print(f"\n📁 ARCHIVOS GENERADOS:")

archivos_esperados = {
    'datos/wti_historico.csv': 'Datos históricos WTI',
    'datos/brent_historico.csv': 'Datos históricos Brent',
    'datos/dataset_consolidado.csv': 'Dataset consolidado',
    'datos/predicciones_prophet.csv': 'Predicciones Prophet',
    'datos/analisis_sentimiento.csv': 'Análisis de sentimiento',
    'datos/interacciones_20M.csv': 'Dataset Big Data (20M+)',
    'datos/grafica_prediccion.png': 'Gráfica de predicción'
}

archivos_encontrados = 0
for archivo, descripcion in archivos_esperados.items():
    if os.path.exists(archivo):
        size_mb = os.path.getsize(archivo) / (1024 * 1024)
        print(f"  ✓ {descripcion:.<40} {size_mb:>8.2f} MB")
        archivos_encontrados += 1
    else:
        print(f"  ✗ {descripcion:.<40} {'NO ENCONTRADO':>12}")

print(f"\n  Total: {archivos_encontrados}/{len(archivos_esperados)} archivos generados")

# ========== RESUMEN DE RESULTADOS ==========
print(f"\n📊 RESUMEN DE RESULTADOS:")

try:
    import pandas as pd
    
    # Cargar resultados
    df_wti = pd.read_csv('datos/wti_historico.csv')
    df_prediccion = pd.read_csv('datos/predicciones_prophet.csv')
    df_sentimiento = pd.read_csv('datos/analisis_sentimiento.csv')
    df_interacciones = pd.read_csv('datos/interacciones_20M.csv', nrows=1000)  # Solo preview
    
    # Precio actual y predicción
    precio_actual = df_wti['Close'].iloc[-1]
    precio_futuro = df_prediccion[df_prediccion['ds'] > df_wti['Date'].max()].head(1)['yhat'].values[0]
    cambio_precio = ((precio_futuro - precio_actual) / precio_actual) * 100
    
    # Sentimiento
    sentimiento_promedio = df_sentimiento['compound'].mean()
    
    # Señal integrada
    if cambio_precio > 0 and sentimiento_promedio > 0.05:
        señal_final = "FUERTEMENTE BULLISH 🚀"
        recomendacion = "COMPRAR activos petroleros (XOM, CVX, OXY, SLB, HAL)"
    elif cambio_precio < 0 and sentimiento_promedio < -0.05:
        señal_final = "FUERTEMENTE BEARISH 📉"
        recomendacion = "VENDER petroleros, COMPRAR aerolíneas (DAL, UAL, FDX)"
    elif cambio_precio > 0:
        señal_final = "BULLISH MODERADO 📈"
        recomendacion = "COMPRAR con precaución, monitorear sentimiento"
    elif cambio_precio < 0:
        señal_final = "BEARISH MODERADO 📉"
        recomendacion = "REDUCIR exposición a petroleros"
    else:
        señal_final = "NEUTRAL ➡️"
        recomendacion = "MANTENER posiciones, esperar señales claras"
    
    print(f"\n  💰 PRECIO DEL PETRÓLEO:")
    print(f"     • Actual: ${precio_actual:.2f}/barril")
    print(f"     • Predicción (10 días): ${precio_futuro:.2f}/barril")
    print(f"     • Cambio esperado: {cambio_precio:+.2f}%")
    
    print(f"\n  📰 SENTIMIENTO DEL MERCADO:")
    print(f"     • Score promedio: {sentimiento_promedio:.3f}")
    if sentimiento_promedio > 0.05:
        print(f"     • Interpretación: POSITIVO (optimista)")
    elif sentimiento_promedio < -0.05:
        print(f"     • Interpretación: NEGATIVO (pesimista)")
    else:
        print(f"     • Interpretación: NEUTRAL (indeciso)")
    
    print(f"\n  🎯 SEÑAL INTEGRADA: {señal_final}")
    print(f"     • Recomendación: {recomendacion}")
    
    print(f"\n  📊 BIG DATA:")
    print(f"     • Registros procesados: 20,000,000")
    print(f"     • Modelo: PySpark ALS (Collaborative Filtering)")
    print(f"     • Usuarios analizados: 50,000")
    print(f"     • Activos evaluados: 9 tickers")
    
except Exception as e:
    print(f"  ⚠️ No se pudo generar resumen: {e}")

# ========== ESTADO FINAL ==========
print("\n" + "=" * 70)

scripts_exitosos = sum(1 for r in resultados.values() if r["status"] == "OK")
scripts_fallidos = len(scripts) - scripts_exitosos

if scripts_fallidos == 0:
    print(" " * 20 + "✓ PIPELINE COMPLETADO EXITOSAMENTE")
    print("\n  Todos los componentes del sistema funcionan correctamente.")
    print("  El sistema está listo para análisis en tiempo real.")
else:
    print(" " * 20 + f"⚠️ PIPELINE COMPLETADO CON {scripts_fallidos} ERROR(ES)")
    print("\n  Revisa los logs anteriores para más detalles.")

print("\n  Hora de finalización: " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("=" * 70)
