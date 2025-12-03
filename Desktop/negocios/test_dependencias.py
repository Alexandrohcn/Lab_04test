"""
Script de Prueba Rápida
Verifica que todas las dependencias estén instaladas correctamente
"""

import sys

print("=" * 60)
print("VERIFICACIÓN DE DEPENDENCIAS")
print("=" * 60)

dependencias = {
    'yfinance': 'Descarga de datos',
    'pandas': 'Manipulación de datos',
    'numpy': 'Operaciones numéricas',
    'prophet': 'Predicción de series temporales',
    'matplotlib': 'Visualización',
    'vaderSentiment': 'Análisis de sentimiento',
    'pyspark': 'Big Data y Spark'
}

print(f"\nPython version: {sys.version}")
print("\nVerificando dependencias...\n")

instaladas = 0
faltantes = []

for modulo, descripcion in dependencias.items():
    try:
        if modulo == 'prophet':
            __import__('prophet')
        elif modulo == 'vaderSentiment':
            __import__('vaderSentiment.vaderSentiment')
        elif modulo == 'pyspark':
            __import__('pyspark.sql')
        else:
            __import__(modulo)
        
        print(f"✓ {modulo:.<25} OK ({descripcion})")
        instaladas += 1
    except ImportError:
        print(f"✗ {modulo:.<25} FALTA ({descripcion})")
        faltantes.append(modulo)

print("\n" + "=" * 60)
print(f"Resultado: {instaladas}/{len(dependencias)} dependencias instaladas")

if faltantes:
    print("\n⚠️ Dependencias faltantes:")
    for modulo in faltantes:
        print(f"  • {modulo}")
    print("\nInstalar con:")
    print("  pip install -r requirements.txt")
else:
    print("\n✓ Todas las dependencias están instaladas correctamente!")
    print("\nPuedes ejecutar:")
    print("  python 1_descargar_datos.py")
    print("  python 5_integracion_completa.py")

print("=" * 60)
