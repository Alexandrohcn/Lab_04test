"""
Script para generar gráficas visuales del sistema
Crea imágenes PNG para usar en la presentación
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Configurar estilo
plt.style.use('dark_background')
sns.set_palette("husl")

# Crear carpeta para gráficas
os.makedirs('graficas_presentacion', exist_ok=True)

print("=" * 70)
print("GENERANDO GRÁFICAS PARA LA PRESENTACIÓN")
print("=" * 70)

# ========== GRÁFICA 1: PRECIOS WTI HISTÓRICOS ==========
print("\n[1/6] Generando gráfica de WTI histórico...")

try:
    df_wti = pd.read_csv('base_datos_csv/petroleo/wti.csv')
    df_wti['Date'] = pd.to_datetime(df_wti['Date'])
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_wti['Date'], df_wti['Close'], linewidth=2, color='#00d4ff', label='WTI')
    ax.fill_between(df_wti['Date'], df_wti['Close'], alpha=0.3, color='#00d4ff')
    
    # Marcar eventos importantes
    covid_date = pd.to_datetime('2020-04-01')
    guerra_date = pd.to_datetime('2022-03-01')
    
    ax.axvline(covid_date, color='#ef4444', linestyle='--', linewidth=2, alpha=0.7, label='COVID-19')
    ax.axvline(guerra_date, color='#f59e0b', linestyle='--', linewidth=2, alpha=0.7, label='Guerra Ucrania')
    
    ax.set_title('Precio Histórico del WTI (2019-2024)', fontsize=16, fontweight='bold', color='white')
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio (USD/barril)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('graficas_presentacion/1_wti_historico.png', dpi=150, facecolor='#0a0e27')
    plt.close()
    print("  ✓ Gráfica WTI guardada")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ========== GRÁFICA 2: PREDICCIÓN PROPHET ==========
print("\n[2/6] Generando gráfica de predicción Prophet...")

try:
    df_pred = pd.read_csv('base_datos_csv/predicciones_prophet.csv')
    df_pred['ds'] = pd.to_datetime(df_pred['ds'])
    
    # Separar datos históricos vs futuros
    ultimo_historico = df_wti['Date'].max()
    df_historico = df_pred[df_pred['ds'] <= ultimo_historico]
    df_futuro = df_pred[df_pred['ds'] > ultimo_historico]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Datos históricos
    ax.plot(df_historico['ds'], df_historico['yhat'], 
            linewidth=2, color='#00d4ff', label='Precio Real')
    
    # Predicción futura
    ax.plot(df_futuro['ds'], df_futuro['yhat'], 
            linewidth=2, color='#10b981', linestyle='--', label='Predicción (30 días)')
    
    # Intervalo de confianza
    ax.fill_between(df_futuro['ds'], 
                     df_futuro['yhat_lower'], 
                     df_futuro['yhat_upper'], 
                     alpha=0.2, color='#10b981', label='Intervalo de confianza')
    
    ax.set_title('Predicción Prophet: WTI a 30 días', fontsize=16, fontweight='bold', color='white')
    ax.set_xlabel('Fecha', fontsize=12)
    ax.set_ylabel('Precio (USD/barril)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.2)
    
    plt.tight_layout()
    plt.savefig('graficas_presentacion/2_prediccion_prophet.png', dpi=150, facecolor='#0a0e27')
    plt.close()
    print("  ✓ Gráfica Predicción guardada")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ========== GRÁFICA 3: DISTRIBUCIÓN DE CLIENTES ==========
print("\n[3/6] Generando gráfica de clientes...")

try:
    df_clientes = pd.read_csv('base_datos_csv/clientes.csv')
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Por tipo de inversor
    tipo_counts = df_clientes['tipo_inversor'].value_counts()
    colors = ['#ef4444', '#f59e0b', '#10b981']
    ax1.pie(tipo_counts.values, labels=tipo_counts.index, autopct='%1.1f%%',
            startangle=90, colors=colors, textprops={'fontsize': 12, 'color': 'white'})
    ax1.set_title('Distribución por Perfil de Inversor', fontsize=14, fontweight='bold', color='white')
    
    # Por ciudad
    ciudad_counts = df_clientes['ciudad'].value_counts().head(7)
    ax2.barh(ciudad_counts.index, ciudad_counts.values, color='#00d4ff')
    ax2.set_title('Clientes por Ciudad (Top 7)', fontsize=14, fontweight='bold', color='white')
    ax2.set_xlabel('Número de Clientes', fontsize=12)
    
    plt.tight_layout()
    plt.savefig('graficas_presentacion/3_distribucion_clientes.png', dpi=150, facecolor='#0a0e27')
    plt.close()
    print("  ✓ Gráfica Clientes guardada")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ========== GRÁFICA 4: COMPARACIÓN EMPRESAS USA vs PERÚ ==========
print("\n[4/6] Generando comparación de empresas...")

try:
    df_usa = pd.read_csv('base_datos_csv/empresas_usa/catalogo.csv')
    df_peru = pd.read_csv('base_datos_csv/empresas_peru/catalogo.csv')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Contar por sector
    sectores = pd.concat([df_usa['sector'], df_peru['sector']]).value_counts()
    
    bars = ax.bar(range(len(sectores)), sectores.values, color='#7c3aed')
    ax.set_xticks(range(len(sectores)))
    ax.set_xticklabels(sectores.index, rotation=45, ha='right')
    ax.set_ylabel('Número de Empresas', fontsize=12)
    ax.set_title('Catálogo de Inversiones por Sector', fontsize=16, fontweight='bold', color='white')
    
    # Añadir valores encima de las barras
    for bar, value in zip(bars, sectores.values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}', ha='center', va='bottom', fontsize=11, color='white')
    
    plt.tight_layout()
    plt.savefig('graficas_presentacion/4_catalogo_empresas.png', dpi=150, facecolor='#0a0e27')
    plt.close()
    print("  ✓ Gráfica Catálogo guardada")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ========== GRÁFICA 5: ANÁLISIS DE SENTIMIENTO ==========
print("\n[5/6] Generando gráfica de sentimiento...")

try:
    df_sent = pd.read_csv('base_datos_csv/sentimientos.csv')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Clasificar por sentimiento
    positivos = len(df_sent[df_sent['clasificacion'] == 'positivo'])
    negativos = len(df_sent[df_sent['clasificacion'] == 'negativo'])
    neutrales = len(df_sent[df_sent['clasificacion'] == 'neutral'])
    
    categorias = ['Positivo 😊', 'Neutral 😐', 'Negativo 😟']
    valores = [positivos, neutrales, negativos]
    colors = ['#10b981', '#6b7280', '#ef4444']
    
    bars = ax.bar(categorias, valores, color=colors, edgecolor='white', linewidth=2)
    ax.set_ylabel('Número de Noticias', fontsize=12)
    ax.set_title('Análisis de Sentimiento: Noticias Financieras', fontsize=16, fontweight='bold', color='white')
    
    # Añadir valores
    for bar, value in zip(bars, valores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(value)}', ha='center', va='bottom', fontsize=14, color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('graficas_presentacion/5_analisis_sentimiento.png', dpi=150, facecolor='#0a0e27')
    plt.close()
    print("  ✓ Gráfica Sentimiento guardada")
except Exception as e:
    print(f"  ✗ Error: {e}")

# ========== GRÁFICA 6: FLUJO DEL SISTEMA (DIAGRAMA) ==========
print("\n[6/6] Generando diagrama de flujo...")

try:
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.axis('off')
    
    # Definir bloques del flujo
    bloques = [
        {'x': 0.1, 'y': 0.7, 'text': '1. DESCARGA\nYahoo Finance\nWTI, Brent, Acciones', 'color': '#00d4ff'},
        {'x': 0.35, 'y': 0.7, 'text': '2. PREDICCIÓN\nProphet ML\n30 días', 'color': '#10b981'},
        {'x': 0.6, 'y': 0.7, 'text': '3. SENTIMIENTO\nVADER NLP\nNoticias', 'color': '#f59e0b'},
        {'x': 0.1, 'y': 0.35, 'text': '4. SEÑAL\nBULLISH/BEARISH', 'color': '#7c3aed'},
        {'x': 0.35, 'y': 0.35, 'text': '5. BIG DATA\nSpark ALS\n20M registros', 'color': '#ef4444'},
        {'x': 0.6, 'y': 0.35, 'text': '6. RECOMENDACIÓN\nTop 5 Activos\nPor cliente', 'color': '#10b981'},
    ]
    
    for bloque in bloques:
        rect = plt.Rectangle((bloque['x'], bloque['y']), 0.2, 0.15, 
                             facecolor=bloque['color'], edgecolor='white', linewidth=2, alpha=0.8)
        ax.add_patch(rect)
        ax.text(bloque['x'] + 0.1, bloque['y'] + 0.075, bloque['text'], 
               ha='center', va='center', fontsize=10, color='white', 
               fontweight='bold', multialignment='center')
    
    # Flechas
    flechas = [
        ((0.3, 0.775), (0.35, 0.775)),
        ((0.55, 0.775), (0.6, 0.775)),
        ((0.2, 0.625), (0.2, 0.5)),
        ((0.45, 0.625), (0.45, 0.5)),
        ((0.3, 0.425), (0.35, 0.425)),
        ((0.55, 0.425), (0.6, 0.425)),
    ]
    
    for inicio, fin in flechas:
        ax.annotate('', xy=fin, xytext=inicio,
                   arrowprops=dict(arrowstyle='->', color='white', lw=2))
    
    ax.set_title('Pipeline del Sistema de Análisis de Petróleo', 
                fontsize=18, fontweight='bold', color='white', y=0.95)
    
    plt.tight_layout()
    plt.savefig('graficas_presentacion/6_flujo_sistema.png', dpi=150, facecolor='#0a0e27')
    plt.close()
    print("  ✓ Diagrama de Flujo guardado")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\n" + "=" * 70)
print("✓ GRÁFICAS GENERADAS")
print("=" * 70)
print("\n📁 Ubicación: graficas_presentacion/")
print("\nGráficas creadas:")
print("  1. 1_wti_historico.png - Precio histórico del WTI")
print("  2. 2_prediccion_prophet.png - Predicción a 30 días")
print("  3. 3_distribucion_clientes.png - Perfiles de clientes")
print("  4. 4_catalogo_empresas.png - Empresas por sector")
print("  5. 5_analisis_sentimiento.png - Sentimiento de noticias")
print("  6. 6_flujo_sistema.png - Diagrama del pipeline")
print("\n💡 Usa estas imágenes en tu presentación para mostrar visualmente el sistema")
print("=" * 70)
