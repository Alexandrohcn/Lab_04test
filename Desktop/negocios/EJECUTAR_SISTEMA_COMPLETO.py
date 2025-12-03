"""
EJECUTAR_SISTEMA_COMPLETO.py
Script único que ejecuta todo el pipeline en orden correcto
con validaciones y reportes profesionales
"""

import os
import sys
import subprocess
from datetime import datetime
import time

print("\n" + "=" * 80)
print("🚀 SISTEMA INTELIGENTE DE ANÁLISIS DE PETRÓLEO")
print("   Ejecución Completa del Pipeline")
print("=" * 80)
print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📂 Directorio: {os.getcwd()}\n")

# Verificar Python
print("🔍 Verificando entorno...")
print(f"   Python: {sys.version.split()[0]}")
print(f"   Sistema: {os.name}")

# Timer general
inicio_total = time.time()

def ejecutar_script(numero, nombre, descripcion, tiempo_estimado=""):
    """Ejecuta un script y retorna si fue exitoso"""
    print("\n" + "-" * 80)
    print(f"[{numero}/6] {descripcion}")
    if tiempo_estimado:
        print(f"⏱️  Tiempo estimado: {tiempo_estimado}")
    print("-" * 80)
    
    inicio = time.time()
    
    try:
        # Ejecutar script
        resultado = subprocess.run(
            [sys.executable, nombre],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        duracion = time.time() - inicio
        
        # Mostrar salida
        if resultado.stdout:
            print(resultado.stdout)
        
        if resultado.returncode == 0:
            print(f"\n✅ Completado exitosamente en {duracion:.1f} segundos")
            return True
        else:
            print(f"\n❌ Error en ejecución (código {resultado.returncode})")
            if resultado.stderr:
                print(f"Error: {resultado.stderr}")
            return False
            
    except Exception as e:
        print(f"\n❌ Excepción: {str(e)}")
        return False

# ========== PIPELINE DE EJECUCIÓN ==========

exitos = []

# PASO 1: Descargar datos
exitos.append(ejecutar_script(
    1, 
    "1_descargar_datos.py",
    "Descargando datos de Yahoo Finance y generando clientes",
    "10-15 minutos"
))

if not exitos[-1]:
    print("\n⚠️  ERROR CRÍTICO: No se pudieron descargar los datos")
    print("   El sistema no puede continuar sin datos base")
    sys.exit(1)

# PASO 2: Validar calidad de datos
exitos.append(ejecutar_script(
    2,
    "0_validar_datos.py",
    "Validando calidad de datos descargados",
    "5-10 segundos"
))

# PASO 3: Predicción con Prophet
exitos.append(ejecutar_script(
    3,
    "2_prediccion_prophet.py",
    "Predicción de precios WTI con Prophet (ML)",
    "30-60 segundos"
))

# PASO 4: Análisis de sentimiento
exitos.append(ejecutar_script(
    4,
    "3_analisis_sentimiento.py",
    "Análisis de sentimiento de noticias con VADER (NLP)",
    "5-10 segundos"
))

# PASO 5: Sistema de recomendación
exitos.append(ejecutar_script(
    5,
    "4_recomendacion_spark.py",
    "Sistema de recomendación con Apache Spark (Big Data)",
    "3-5 minutos"
))

# PASO 6: Generar gráficas
if os.path.exists("generar_graficas.py"):
    exitos.append(ejecutar_script(
        6,
        "generar_graficas.py",
        "Generando visualizaciones profesionales",
        "30-60 segundos"
    ))
else:
    print("\n⚠️  Script generar_graficas.py no encontrado, saltando...")
    exitos.append(True)  # No es crítico

# ========== REPORTE FINAL ==========

duracion_total = time.time() - inicio_total
minutos = int(duracion_total // 60)
segundos = int(duracion_total % 60)

print("\n" + "=" * 80)
print("📊 REPORTE FINAL DE EJECUCIÓN")
print("=" * 80)

print(f"\n⏱️  Tiempo total: {minutos} minutos, {segundos} segundos")

print(f"\n📈 Resultados por módulo:")
modulos = [
    "Descarga de datos",
    "Validación de calidad",
    "Predicción Prophet",
    "Análisis sentimiento",
    "Recomendación Spark",
    "Generación gráficas"
]

for i, (modulo, exito) in enumerate(zip(modulos, exitos), 1):
    estado = "✅ EXITOSO" if exito else "❌ FALLIDO"
    print(f"   [{i}/6] {modulo:25s} {estado}")

# Contar éxitos
total_exitos = sum(exitos)
total_modulos = len(exitos)

print(f"\n🎯 Tasa de éxito: {total_exitos}/{total_modulos} ({total_exitos/total_modulos*100:.0f}%)")

if total_exitos == total_modulos:
    print("\n🎉 ¡SISTEMA EJECUTADO COMPLETAMENTE CON ÉXITO!")
    print("\n📁 Archivos generados:")
    print("   • base_datos_csv/petroleo/wti.csv")
    print("   • base_datos_csv/clientes.csv")
    print("   • base_datos_csv/predicciones_prophet.csv")
    print("   • base_datos_csv/sentimientos.csv")
    print("   • base_datos_csv/señal_mercado.csv")
    print("   • base_datos_csv/recomendaciones.csv")
    print("   • base_datos_csv/interacciones_20M.csv (~400 MB)")
    print("   • base_datos_csv/quality_report.txt")
    
    if os.path.exists("graficas_presentacion"):
        print("   • graficas_presentacion/*.png")
    
    print("\n📖 Siguiente paso:")
    print("   → Revisar: base_datos_csv/señal_mercado.csv")
    print("   → Revisar: base_datos_csv/quality_report.txt")
    print("   → Demo: python DEMO_sistema_recomendacion.py")
    
elif total_exitos >= 4:
    print("\n⚠️  EJECUCIÓN PARCIAL")
    print("   El sistema básico está funcionando, pero algunos módulos fallaron")
    print("   Revisa los errores arriba para más detalles")
else:
    print("\n❌ MÚLTIPLES FALLOS DETECTADOS")
    print("   Revisa los errores arriba y ejecuta:")
    print("   → python instalar_dependencias.py")
    print("   → python test_dependencias.py")

print("\n" + "=" * 80)

# Mostrar valores reales de la última ejecución
print("\n💎 VALORES REALES GENERADOS:")
print("=" * 80)

try:
    import pandas as pd
    
    # Leer señal de mercado
    if os.path.exists('base_datos_csv/señal_mercado.csv'):
        df_señal = pd.read_csv('base_datos_csv/señal_mercado.csv')
        if len(df_señal) > 0:
            ultima = df_señal.iloc[-1]
            print(f"\n📊 SEÑAL DE MERCADO:")
            print(f"   Precio actual WTI: ${ultima['precio_actual']:.2f}")
            print(f"   Precio predicho: ${ultima['precio_predicho']:.2f}")
            print(f"   Cambio esperado: {ultima['cambio_porcentual']:+.2f}%")
            print(f"   Sentimiento: {ultima['sentimiento_promedio']:+.3f}")
            print(f"   Señal: {ultima['señal']}")
            print(f"   🎯 RECOMENDACIÓN: {ultima['recomendacion']}")
    
    # Estadísticas de recomendaciones
    if os.path.exists('base_datos_csv/recomendaciones.csv'):
        df_recs = pd.read_csv('base_datos_csv/recomendaciones.csv')
        print(f"\n💼 RECOMENDACIONES GENERADAS:")
        print(f"   Total: {len(df_recs):,} recomendaciones")
        print(f"   Clientes únicos: {df_recs['cliente_id'].nunique():,}")
        print(f"   Score promedio: {df_recs['score'].mean():.2f}/5.0")
        print(f"   Score máximo: {df_recs['score'].max():.2f}/5.0")
    
    # Datos WTI
    if os.path.exists('base_datos_csv/petroleo/wti.csv'):
        df_wti = pd.read_csv('base_datos_csv/petroleo/wti.csv')
        print(f"\n🛢️  DATOS WTI:")
        print(f"   Registros históricos: {len(df_wti):,}")
        print(f"   Rango de fechas: {df_wti['fecha'].min()} a {df_wti['fecha'].max()}")
        print(f"   Precio promedio: ${df_wti['precio_cierre'].mean():.2f}")
        print(f"   Precio mínimo: ${df_wti['precio_cierre'].min():.2f}")
        print(f"   Precio máximo: ${df_wti['precio_cierre'].max():.2f}")

except Exception as e:
    print(f"\n⚠️  No se pudieron leer estadísticas: {e}")

print("\n" + "=" * 80)
print("✨ Sistema listo para presentación")
print("=" * 80 + "\n")

# Exit code
sys.exit(0 if total_exitos == total_modulos else 1)
