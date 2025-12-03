"""
Script de Instalación Rápida
Instala las dependencias necesarias
"""

import subprocess
import sys

print("=" * 60)
print("INSTALANDO DEPENDENCIAS")
print("=" * 60)

dependencias = [
    'yfinance',
    'pandas',
    'numpy',
    'prophet',
    'matplotlib',
    'vaderSentiment',
    'pyspark'
]

print("\nInstalando paquetes...")
for paquete in dependencias:
    print(f"\n→ Instalando {paquete}...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', paquete, '-q'])
        print(f"  ✓ {paquete} instalado")
    except:
        print(f"  ⚠️ Error instalando {paquete}")

print("\n" + "=" * 60)
print("INSTALACIÓN COMPLETADA")
print("=" * 60)
print("\nAhora puedes ejecutar:")
print("  python 1_descargar_datos.py")
