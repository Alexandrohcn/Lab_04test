"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║           SISTEMA DE RECOMENDACIÓN INTELIGENTE DE PETRÓLEO                   ║
║                                                                              ║
║   Sistema cuantitativo profesional para trading de WTI y Brent              ║
║   Basado en: Análisis Técnico + Sentimiento + Predicción ML                 ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

EJECUCIÓN:
    python SISTEMA_RECOMENDACION_PETROLEO.py

SALIDA EN TERMINAL:
    ✓ Recomendación del día (COMPRAR/VENDER/MANTENER)
    ✓ Razones detalladas (sentimiento + tendencia + predicción)
    ✓ Termómetro de riesgo (BAJO/MEDIO/ALTO)
    ✓ Noticias relevantes del día
    ✓ Comparación WTI vs. Brent
    ✓ Nivel de confianza del modelo

GRÁFICAS GENERADAS:
    • recomendacion_diaria.png (dashboard completo)
    • prediccion_wti_brent.png (comparación visual)
    • termometro_riesgo.png (indicador visual)
"""

import warnings
warnings.filterwarnings('ignore')

import os
import sys
from datetime import datetime, timedelta
import time

print("\n🔧 Inicializando Sistema de Recomendación Inteligente...")

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTACIONES
# ══════════════════════════════════════════════════════════════════════════════

try:
    import pandas as pd
    import numpy as np
    import yfinance as yf
    from prophet import Prophet
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import Rectangle, FancyBboxPatch
    import seaborn as sns
    print("✓ Bibliotecas importadas correctamente")
except ImportError as e:
    print(f"❌ Error: {e}")
    print("Ejecuta: pip install pandas numpy yfinance prophet matplotlib seaborn")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════════════════════

PERIODO_HISTORICO = "1y"  # Período de datos históricos (1y, 2y, 5y, 10y)
DIAS_PREDICCION = 10      # Días a predecir hacia adelante
GRAFICAS_DIR = "graficas_recomendacion"

os.makedirs(GRAFICAS_DIR, exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1: DESCARGA Y PREPARACIÓN DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def descargar_datos_petroleo():
    """
    Descarga datos REALES de WTI y Brent desde Yahoo Finance
    
    RETORNA:
        df_wti: DataFrame con precios WTI
        df_brent: DataFrame con precios Brent
    """
    print("\n" + "="*80)
    print("MÓDULO 1: DESCARGA DE DATOS REALES")
    print("="*80)
    
    print(f"\n[1.1] Descargando WTI ({PERIODO_HISTORICO})...")
    
    # WTI = "CL=F" (Crude Oil Futures)
    wti = yf.Ticker("CL=F")
    df_wti = wti.history(period=PERIODO_HISTORICO)
    df_wti.reset_index(inplace=True)
    df_wti = df_wti[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
    df_wti.columns = ['fecha', 'precio', 'maximo', 'minimo', 'apertura', 'volumen']
    
    print(f"  ✓ WTI: {len(df_wti)} días descargados")
    print(f"    Precio actual: ${df_wti['precio'].iloc[-1]:.2f}/barril")
    
    print(f"\n[1.2] Descargando Brent ({PERIODO_HISTORICO})...")
    
    # Brent = "BZ=F"
    brent = yf.Ticker("BZ=F")
    df_brent = brent.history(period=PERIODO_HISTORICO)
    df_brent.reset_index(inplace=True)
    df_brent = df_brent[['Date', 'Close', 'High', 'Low', 'Open', 'Volume']]
    df_brent.columns = ['fecha', 'precio', 'maximo', 'minimo', 'apertura', 'volumen']
    
    print(f"  ✓ Brent: {len(df_brent)} días descargados")
    print(f"    Precio actual: ${df_brent['precio'].iloc[-1]:.2f}/barril")
    
    # Calcular spread WTI-Brent
    spread = df_brent['precio'].iloc[-1] - df_wti['precio'].iloc[-1]
    print(f"\n  📊 Spread Brent-WTI: ${spread:+.2f}")
    
    return df_wti, df_brent

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2: ANÁLISIS TÉCNICO
# ══════════════════════════════════════════════════════════════════════════════

def calcular_indicadores_tecnicos(df):
    """
    Calcula indicadores técnicos profesionales
    
    INDICADORES:
        - SMA 20 y 50 (promedios móviles simples)
        - EMA 12 y 26 (promedios móviles exponenciales)
        - RSI (Relative Strength Index)
        - Soportes y resistencias
    
    RETORNA:
        df con columnas adicionales de indicadores
        señal_tecnica: dict con análisis técnico
    """
    print("\n" + "="*80)
    print("MÓDULO 2: ANÁLISIS TÉCNICO")
    print("="*80)
    
    print("\n[2.1] Calculando promedios móviles...")
    
    # SMA (Simple Moving Average)
    df['SMA_20'] = df['precio'].rolling(window=20).mean()
    df['SMA_50'] = df['precio'].rolling(window=50).mean()
    
    # EMA (Exponential Moving Average)
    df['EMA_12'] = df['precio'].ewm(span=12, adjust=False).mean()
    df['EMA_26'] = df['precio'].ewm(span=26, adjust=False).mean()
    
    precio_actual = df['precio'].iloc[-1]
    sma20 = df['SMA_20'].iloc[-1]
    sma50 = df['SMA_50'].iloc[-1]
    
    print(f"  Precio actual: ${precio_actual:.2f}")
    print(f"  SMA 20 días: ${sma20:.2f}")
    print(f"  SMA 50 días: ${sma50:.2f}")
    
    # Determinar tendencia
    if precio_actual > sma20 > sma50:
        tendencia = "ALCISTA"
        tendencia_icono = "📈"
    elif precio_actual < sma20 < sma50:
        tendencia = "BAJISTA"
        tendencia_icono = "📉"
    else:
        tendencia = "LATERAL"
        tendencia_icono = "➡️"
    
    print(f"  {tendencia_icono} Tendencia: {tendencia}")
    
    print("\n[2.2] Calculando RSI (14 períodos)...")
    
    # RSI = Relative Strength Index
    delta = df['precio'].diff()
    ganancia = delta.where(delta > 0, 0)
    perdida = -delta.where(delta < 0, 0)
    
    avg_ganancia = ganancia.rolling(window=14).mean()
    avg_perdida = perdida.rolling(window=14).mean()
    
    rs = avg_ganancia / avg_perdida
    rsi = 100 - (100 / (1 + rs))
    df['RSI'] = rsi
    
    rsi_actual = rsi.iloc[-1]
    print(f"  RSI actual: {rsi_actual:.1f}")
    
    if rsi_actual > 70:
        rsi_señal = "SOBRECOMPRADO"
        rsi_icono = "⚠️"
    elif rsi_actual < 30:
        rsi_señal = "SOBREVENDIDO"
        rsi_icono = "✅"
    else:
        rsi_señal = "NEUTRAL"
        rsi_icono = "➡️"
    
    print(f"  {rsi_icono} Condición RSI: {rsi_señal}")
    
    print("\n[2.3] Identificando soportes y resistencias...")
    
    # Soporte: mínimo de últimos 20 días
    # Resistencia: máximo de últimos 20 días
    soporte = df['minimo'].tail(20).min()
    resistencia = df['maximo'].tail(20).max()
    
    print(f"  Soporte cercano: ${soporte:.2f}")
    print(f"  Resistencia cercana: ${resistencia:.2f}")
    
    # Calcular distancia a soporte/resistencia
    dist_soporte = ((precio_actual - soporte) / soporte) * 100
    dist_resistencia = ((resistencia - precio_actual) / precio_actual) * 100
    
    print(f"  Distancia a soporte: {dist_soporte:.1f}%")
    print(f"  Distancia a resistencia: {dist_resistencia:.1f}%")
    
    # SEÑAL TÉCNICA INTEGRADA
    señal_tecnica = {
        'tendencia': tendencia,
        'rsi': rsi_actual,
        'rsi_señal': rsi_señal,
        'soporte': soporte,
        'resistencia': resistencia,
        'precio_vs_sma20': ((precio_actual - sma20) / sma20) * 100,
        'precio_vs_sma50': ((precio_actual - sma50) / sma50) * 100
    }
    
    return df, señal_tecnica

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3: PREDICCIÓN CON PROPHET
# ══════════════════════════════════════════════════════════════════════════════

def generar_prediccion(df, dias=10):
    """
    Genera predicción de precios con Prophet
    
    ENTRADA:
        df: DataFrame con columnas 'fecha' y 'precio'
        dias: número de días a predecir
    
    RETORNA:
        forecast: DataFrame con predicciones
        metricas: dict con RMSE y confianza del modelo
    """
    print("\n" + "="*80)
    print("MÓDULO 3: PREDICCIÓN CON MACHINE LEARNING")
    print("="*80)
    
    print(f"\n[3.1] Preparando datos para Prophet...")
    
    # Prophet requiere columnas 'ds' (fecha) y 'y' (valor)
    df_prophet = df[['fecha', 'precio']].copy()
    df_prophet.columns = ['ds', 'y']
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
    
    # Prophet requiere fechas sin timezone
    if df_prophet['ds'].dt.tz is not None:
        df_prophet['ds'] = df_prophet['ds'].dt.tz_localize(None)
    
    print(f"  Datos de entrenamiento: {len(df_prophet)} días")
    
    print(f"\n[3.2] Entrenando modelo Prophet...")
    
    # Crear y entrenar modelo
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True,
        changepoint_prior_scale=0.05  # sensibilidad a cambios de tendencia
    )
    model.fit(df_prophet)
    
    print(f"  ✓ Modelo entrenado")
    
    print(f"\n[3.3] Generando predicción ({dias} días)...")
    
    # Crear fechas futuras
    future = model.make_future_dataframe(periods=dias)
    forecast = model.predict(future)
    
    # Extraer solo predicciones futuras
    forecast_futuro = forecast[forecast['ds'] > df_prophet['ds'].max()].copy()
    forecast_futuro = forecast_futuro[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast_futuro.columns = ['fecha', 'prediccion', 'limite_inf', 'limite_sup']
    
    precio_actual = df['precio'].iloc[-1]
    precio_predicho = forecast_futuro['prediccion'].iloc[-1]  # último día predicho
    cambio = ((precio_predicho - precio_actual) / precio_actual) * 100
    
    print(f"  Precio actual: ${precio_actual:.2f}")
    print(f"  Predicción {dias} días: ${precio_predicho:.2f}")
    print(f"  Cambio esperado: {cambio:+.2f}%")
    
    # Calcular confianza basada en ancho del intervalo
    intervalo_avg = (forecast_futuro['limite_sup'] - forecast_futuro['limite_inf']).mean()
    confianza = max(0, min(100, 100 - (intervalo_avg / precio_actual) * 100))
    
    print(f"  Confianza del modelo: {confianza:.0f}%")
    
    metricas = {
        'cambio_porcentual': cambio,
        'precio_predicho': precio_predicho,
        'confianza': confianza
    }
    
    return forecast_futuro, metricas

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4: ANÁLISIS DE SENTIMIENTO PROFESIONAL (HISTÓRICO Y PERSISTENTE)
# ══════════════════════════════════════════════════════════════════════════════

def descargar_y_gestionar_noticias_historicas():
    """
    Descarga noticias, las filtra, pondera y guarda en base histórica persistente.
    
    CARACTERÍSTICAS:
    - Persistencia: Acumula noticias en 'base_datos_csv/noticias_historico.csv'
    - Filtrado: Solo guarda noticias con palabras clave relevantes
    - Ponderación: Asigna peso según confiabilidad de la fuente
    """
    print("\n[4.1] Gestionando Base de Datos de Noticias...")
    
    # Configuración
    ARCHIVO_HISTORICO = "base_datos_csv/noticias_historico.csv"
    os.makedirs("base_datos_csv", exist_ok=True)
    
    KEYWORDS = ['oil', 'crude', 'wti', 'brent', 'opec', 'barrel', 'energy', 'supply', 'demand']
    
    FUENTES_PESOS = {
        'Reuters': 1.0, 'Bloomberg': 1.0, 'OPEC': 0.95, 'EIA': 0.95,
        'Yahoo Finance': 0.7, 'Google News': 0.6, 'CNBC': 0.7
    }
    
    # 1. Cargar base existente
    required_columns = ['fecha', 'titulo', 'fuente', 'link', 'peso']
    if os.path.exists(ARCHIVO_HISTORICO):
        try:
            df_hist = pd.read_csv(ARCHIVO_HISTORICO)
            # Validar columnas
            if not all(col in df_hist.columns for col in required_columns):
                print("  ⚠️ Base histórica con formato antiguo. Regenerando...")
                df_hist = pd.DataFrame(columns=required_columns)
            else:
                df_hist['fecha'] = pd.to_datetime(df_hist['fecha'])
                print(f"  📂 Base histórica cargada: {len(df_hist)} noticias")
        except Exception as e:
            print(f"  ⚠️ Error leyendo base histórica: {e}. Creando nueva.")
            df_hist = pd.DataFrame(columns=required_columns)
    else:
        print("  📂 Creando nueva base histórica...")
        df_hist = pd.DataFrame(columns=required_columns)

    # 2. Descargar nuevas noticias (Google News + Yahoo Finance)
    nuevas_noticias = []
    
    # --- Google News (Búsqueda Histórica) ---
    try:
        import requests
        from bs4 import BeautifulSoup
        
        # Intentar buscar noticias de los últimos 2 meses si la base es pequeña
        if len(df_hist) < 100:
            print("  🔍 Base pequeña. Iniciando búsqueda histórica profunda (2 meses)...")
            fechas_busqueda = [
                datetime.now().strftime('%Y-%m-%d'),
                (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d'),
                (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                (datetime.now() - timedelta(days=45)).strftime('%Y-%m-%d'),
                (datetime.now() - timedelta(days=60)).strftime('%Y-%m-%d')
            ]
        else:
            fechas_busqueda = [datetime.now().strftime('%Y-%m-%d')]

        for fecha_corte in fechas_busqueda:
            # Query con fecha para intentar traer cosas diferentes
            # Nota: RSS de Google News no respeta estrictamente 'after:', pero variando el query ayuda
            queries = [
                f"oil prices WTI after:{fecha_corte}",
                "crude oil market",
                "OPEC decision",
                "Brent crude price"
            ]
            
            for q in queries:
                url = f"https://news.google.com/rss/search?q={q.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
                try:
                    response = requests.get(url, timeout=5)
                    # Intentar parser lxml, fallback a html.parser
                    try:
                        soup = BeautifulSoup(response.content, 'xml')
                    except:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                    items = soup.find_all('item')
                    
                    for item in items:
                        titulo = item.find('title').text if item.find('title') else ""
                        fecha_str = item.find('pubDate').text if item.find('pubDate') else ""
                        link = item.find('link').text if item.find('link') else ""
                        
                        try:
                            fecha = pd.to_datetime(fecha_str).strftime('%Y-%m-%d')
                        except:
                            fecha = fecha_corte # Usar la fecha de búsqueda como fallback aproximado
                        
                        nuevas_noticias.append({
                            'fecha': fecha, 'titulo': titulo, 'fuente': 'Google News',
                            'link': link, 'peso': FUENTES_PESOS.get('Google News', 0.6)
                        })
                except Exception as e:
                    print(f"    ⚠️ Error query '{q}': {e}")
                
                time.sleep(0.5) # Pausa para no saturar

    except Exception as e:
        print(f"  ⚠️ Error General Google News: {e}")

    # --- Yahoo Finance ---
    try:
        tickers = ["CL=F", "BZ=F", "XOM", "CVX"] # Más tickers para más noticias
        for t in tickers:
            try:
                oil = yf.Ticker(t)
                news = oil.news
                for item in news:
                    titulo = item.get('title', '')
                    ts = item.get('providerPublishTime', time.time())
                    fecha = datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                    publisher = item.get('publisher', 'Yahoo Finance')
                    
                    nuevas_noticias.append({
                        'fecha': fecha, 'titulo': titulo, 'fuente': publisher,
                        'link': item.get('link', ''),
                        'peso': FUENTES_PESOS.get(publisher, 0.7)
                    })
            except:
                continue
    except Exception as e:
        print(f"  ⚠️ Error Yahoo Finance: {e}")

    # 3. Filtrar y procesar nuevas
    if nuevas_noticias:
        df_nuevas = pd.DataFrame(nuevas_noticias)
        
        # Filtrado por keywords (Más relajado: busca en título O si viene de ticker relevante)
        # Si viene de Yahoo Finance (CL=F), asumimos relevancia aunque no diga "oil"
        def es_relevante(row):
            texto = str(row['titulo']).lower()
            if any(k in texto for k in KEYWORDS):
                return True
            if row['fuente'] == 'Yahoo Finance': # Asumir relevancia por ticker
                return True
            return False

        df_nuevas = df_nuevas[df_nuevas.apply(es_relevante, axis=1)]
        
        if not df_nuevas.empty:
            df_nuevas['fecha'] = pd.to_datetime(df_nuevas['fecha'])
            
            # Combinar y deduplicar
            df_total = pd.concat([df_hist, df_nuevas], ignore_index=True)
            df_total = df_total.drop_duplicates(subset=['titulo'], keep='first')
            df_total = df_total.sort_values('fecha', ascending=False)
            
            # Guardar
            df_total.to_csv(ARCHIVO_HISTORICO, index=False)
            print(f"  💾 Base actualizada: {len(df_total)} noticias (Agregadas: {len(df_total) - len(df_hist)})")
            return df_total
        else:
            print("  ⚠️ Ninguna noticia nueva relevante pasó el filtro.")
            return df_hist
    else:
        print("  ⚠️ No se descargaron noticias nuevas.")
        return df_hist

def analizar_sentimiento_mercado(df_wti):
    """
    Analiza sentimiento usando base histórica y calcula correlación con precio.
    """
    print("\n" + "="*80)
    print("MÓDULO 4: ANÁLISIS DE SENTIMIENTO AVANZADO")
    print("="*80)
    
    # 1. Obtener base histórica actualizada
    df_noticias = descargar_y_gestionar_noticias_historicas()
    
    if df_noticias.empty:
        print("  ⚠️ Sin noticias para analizar.")
        return 0.0, [], None

    # 2. Análisis VADER
    print("\n[4.2] Calculando sentimiento (VADER)...")
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        
        # Calcular score si no existe o recalcular
        if 'score' not in df_noticias.columns:
            df_noticias['score'] = df_noticias['titulo'].apply(lambda x: analyzer.polarity_scores(str(x))['compound'])
        
        # Aplicar peso de la fuente
        df_noticias['score_ponderado'] = df_noticias['score'] * df_noticias['peso']
        
    except ImportError:
        print("  ⚠️ vaderSentiment no instalado. Usando scores neutros.")
        df_noticias['score'] = 0.0
        df_noticias['score_ponderado'] = 0.0

    # 3. Agrupación diaria y Rolling Window
    df_diario = df_noticias.groupby('fecha')['score_ponderado'].mean().reset_index()
    df_diario = df_diario.sort_values('fecha')
    df_diario['rolling_7d'] = df_diario['score_ponderado'].rolling(window=7, min_periods=1).mean()
    
    # Sentimiento actual (último rolling 7d o promedio de hoy)
    if not df_diario.empty:
        sentimiento_score = df_diario['rolling_7d'].iloc[-1]
    else:
        sentimiento_score = 0.0

    print(f"  ✓ Sentimiento Actual (Rolling 7d): {sentimiento_score:+.4f}")
    print(f"  ✓ Noticias en base: {len(df_noticias)}")

    # 4. Correlación con Precio (si hay suficientes datos)
    print("\n[4.3] Analizando correlación Precio-Sentimiento...")
    
    # Asegurar tipos datetime para merge
    df_wti['fecha'] = pd.to_datetime(df_wti['fecha'])
    df_diario['fecha'] = pd.to_datetime(df_diario['fecha'])
    
    # Eliminar timezone si existe para evitar conflictos
    if df_wti['fecha'].dt.tz is not None:
        df_wti['fecha'] = df_wti['fecha'].dt.tz_localize(None)
    if df_diario['fecha'].dt.tz is not None:
        df_diario['fecha'] = df_diario['fecha'].dt.tz_localize(None)
        
    df_corr = pd.merge(df_wti[['fecha', 'precio']], df_diario, on='fecha', how='inner')
    
    if len(df_corr) > 5:
        correlacion = df_corr['precio'].corr(df_corr['rolling_7d'])
        print(f"  📊 Correlación Pearson (Precio vs Sentimiento 7d): {correlacion:+.2f}")
    else:
        print("  ⚠️ Insuficientes datos coincidentes para correlación.")
        correlacion = 0.0

    # Top noticias para mostrar
    noticias_relevantes = []
    # Convertir a lista de dicts
    recientes = df_noticias.head(10) # Las más recientes ya que ordenamos por fecha desc
    
    # Top positiva y negativa de las recientes
    top_pos = recientes.nlargest(1, 'score')
    top_neg = recientes.nsmallest(1, 'score')
    
    if not top_pos.empty:
        r = top_pos.iloc[0]
        noticias_relevantes.append({'texto': r['titulo'], 'score': r['score'], 'tipo': 'POSITIVA'})
    if not top_neg.empty:
        r = top_neg.iloc[0]
        noticias_relevantes.append({'texto': r['titulo'], 'score': r['score'], 'tipo': 'NEGATIVA'})
        
    # Rellenar con recientes
    for _, row in recientes.head(3).iterrows():
        if row['titulo'] not in [n['texto'] for n in noticias_relevantes]:
            tipo = 'POSITIVA' if row['score'] > 0.05 else 'NEGATIVA' if row['score'] < -0.05 else 'NEUTRAL'
            noticias_relevantes.append({'texto': row['titulo'], 'score': row['score'], 'tipo': tipo})
            
    return sentimiento_score, noticias_relevantes, df_diario

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5: MOTOR DE RECOMENDACIÓN INTELIGENTE
# ══════════════════════════════════════════════════════════════════════════════

def generar_recomendacion(señal_tecnica, metricas_prediccion, sentimiento_score):
    """
    Motor principal que integra todas las señales y genera recomendación final
    
    FÓRMULA DE DECISIÓN:
        Score = 0.40 × Predicción + 0.30 × Técnico + 0.30 × Sentimiento
    
    DECISIÓN:
        Score ≥ 0.65  → COMPRAR FUERTE
        Score ≥ 0.55  → COMPRAR
        0.45 < Score < 0.55 → MANTENER
        Score ≤ 0.45  → VENDER
        Score ≤ 0.35  → VENDER FUERTE
    
    RETORNA:
        recomendacion: dict con decisión final y razones
    """
    print("\n" + "="*80)
    print("MÓDULO 5: MOTOR DE RECOMENDACIÓN INTELIGENTE")
    print("="*80)
    
    print("\n[5.1] Integrando señales...")
    
    # ─────────────────────────────────────────────────────────────────────────
    # NORMALIZAR SEÑALES A [0, 1]
    # ─────────────────────────────────────────────────────────────────────────
    
    # 1. Señal de PREDICCIÓN
    cambio = metricas_prediccion['cambio_porcentual']
    # Normalizar cambio esperado: -10% → 0, +10% → 1
    pred_norm = (cambio + 10) / 20
    pred_norm = max(0, min(1, pred_norm))  # clip a [0, 1]
    
    # 2. Señal TÉCNICA
    # Combinar tendencia + RSI
    if señal_tecnica['tendencia'] == "ALCISTA":
        tecnico_tendencia = 0.7
    elif señal_tecnica['tendencia'] == "BAJISTA":
        tecnico_tendencia = 0.3
    else:
        tecnico_tendencia = 0.5
    
    # RSI: normalizar [0, 100] → [0, 1]
    tecnico_rsi = señal_tecnica['rsi'] / 100
    
    # Combinar (50% tendencia, 50% RSI)
    tecnico_norm = 0.5 * tecnico_tendencia + 0.5 * tecnico_rsi
    
    # 3. Señal de SENTIMIENTO
    # Convertir [-1, +1] → [0, 1]
    sent_norm = (sentimiento_score + 1) / 2
    
    print(f"  Predicción normalizada: {pred_norm:.2f}")
    print(f"  Técnico normalizado: {tecnico_norm:.2f}")
    print(f"  Sentimiento normalizado: {sent_norm:.2f}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # FÓRMULA DE INTEGRACIÓN
    # ─────────────────────────────────────────────────────────────────────────
    
    PESO_PREDICCION = 0.40
    PESO_TECNICO = 0.30
    PESO_SENTIMIENTO = 0.30
    
    score_final = (PESO_PREDICCION * pred_norm + 
                   PESO_TECNICO * tecnico_norm + 
                   PESO_SENTIMIENTO * sent_norm)
    
    print(f"\n[5.2] Score final integrado: {score_final:.3f}")
    
    # ─────────────────────────────────────────────────────────────────────────
    # DECISIÓN FINAL
    # ─────────────────────────────────────────────────────────────────────────
    
    if score_final >= 0.65:
        accion = "COMPRAR FUERTE"
        accion_icono = "🟢🟢"
        riesgo = "MEDIO-ALTO"
        color_riesgo = "yellow"
    elif score_final >= 0.55:
        accion = "COMPRAR"
        accion_icono = "🟢"
        riesgo = "MEDIO"
        color_riesgo = "green"
    elif score_final > 0.45:
        accion = "MANTENER"
        accion_icono = "🟡"
        riesgo = "BAJO"
        color_riesgo = "blue"
    elif score_final > 0.35:
        accion = "VENDER"
        accion_icono = "🔴"
        riesgo = "MEDIO"
        color_riesgo = "orange"
    else:
        accion = "VENDER FUERTE"
        accion_icono = "🔴🔴"
        riesgo = "ALTO"
        color_riesgo = "red"
    
    # ─────────────────────────────────────────────────────────────────────────
    # RAZONES DETALLADAS
    # ─────────────────────────────────────────────────────────────────────────
    
    razones = []
    
    # Razón 1: Predicción
    if cambio > 0:
        razones.append(f"✓ Predicción alcista: +{cambio:.1f}% en {DIAS_PREDICCION} días")
    else:
        razones.append(f"✗ Predicción bajista: {cambio:.1f}% en {DIAS_PREDICCION} días")
    
    # Razón 2: Tendencia técnica
    razones.append(f"{'✓' if señal_tecnica['tendencia'] == 'ALCISTA' else '✗'} Tendencia {señal_tecnica['tendencia'].lower()}")
    
    # Razón 3: RSI
    if señal_tecnica['rsi_señal'] == "SOBREVENDIDO":
        razones.append(f"✓ RSI {señal_tecnica['rsi']:.0f} (sobrevendido, oportunidad)")
    elif señal_tecnica['rsi_señal'] == "SOBRECOMPRADO":
        razones.append(f"✗ RSI {señal_tecnica['rsi']:.0f} (sobrecomprado, precaución)")
    else:
        razones.append(f"➡️ RSI {señal_tecnica['rsi']:.0f} (neutral)")
    
    # Razón 4: Sentimiento
    if sentimiento_score > 0.2:
        razones.append(f"✓ Sentimiento positivo ({sentimiento_score:+.2f})")
    elif sentimiento_score < -0.2:
        razones.append(f"✗ Sentimiento negativo ({sentimiento_score:+.2f})")
    else:
        razones.append(f"➡️ Sentimiento neutral ({sentimiento_score:+.2f})")
    
    # Razón 5: Confianza del modelo
    razones.append(f"ℹ️ Confianza del modelo: {metricas_prediccion['confianza']:.0f}%")
    
    recomendacion = {
        'accion': accion,
        'accion_icono': accion_icono,
        'score': score_final,
        'riesgo': riesgo,
        'color_riesgo': color_riesgo,
        'razones': razones,
        'confianza': metricas_prediccion['confianza']
    }
    
    return recomendacion

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 6: VISUALIZACIÓN DE RESULTADOS
# ══════════════════════════════════════════════════════════════════════════════

def generar_dashboard(df_wti, df_brent, forecast, señal_tecnica, recomendacion, noticias, df_sentimiento_diario=None):
    """
    Genera dashboard visual con todos los componentes, incluyendo correlación precio-sentimiento.
    """
    print("\n" + "="*80)
    print("MÓDULO 6: GENERANDO VISUALIZACIONES PROFESIONALES")
    print("="*80)
    
    print("\n[6.1] Creando dashboard principal...")
    
    fig = plt.figure(figsize=(16, 12)) # Aumentamos altura para mejor visualización
    
    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 1: Predicción WTI con SMA
    # ─────────────────────────────────────────────────────────────────────────
    ax1 = plt.subplot(3, 2, 1) # 3 filas, 2 columnas
    ax1.plot(df_wti['fecha'], df_wti['precio'], 'o-', color='black', linewidth=1.5, markersize=2, label='WTI Real', alpha=0.7)
    ax1.plot(df_wti['fecha'], df_wti['SMA_20'], '--', color='blue', linewidth=1, label='SMA 20', alpha=0.6)
    ax1.plot(forecast['fecha'], forecast['prediccion'], 's-', color='#2ecc71', linewidth=2, markersize=4, label='Predicción')
    ax1.fill_between(forecast['fecha'], forecast['limite_inf'], forecast['limite_sup'], color='#2ecc71', alpha=0.2)
    ax1.set_title('Predicción WTI + Técnico', fontsize=11, fontweight='bold')
    ax1.legend(loc='best', fontsize=8)
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='x', rotation=45)

    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 2: Comparación WTI vs Brent
    # ─────────────────────────────────────────────────────────────────────────
    ax2 = plt.subplot(3, 2, 2)
    ax2.plot(df_wti['fecha'], df_wti['precio'], '-', color='#3498db', linewidth=2, label='WTI')
    ax2.plot(df_brent['fecha'], df_brent['precio'], '-', color='#e67e22', linewidth=2, label='Brent')
    spread = df_brent['precio'].iloc[-1] - df_wti['precio'].iloc[-1]
    ax2.text(0.02, 0.95, f'Spread: ${spread:+.2f}', transform=ax2.transAxes, fontsize=9, fontweight='bold', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    ax2.set_title('WTI vs Brent', fontsize=11, fontweight='bold')
    ax2.legend(loc='best', fontsize=8)
    ax2.grid(True, alpha=0.3)

    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 3: CORRELACIÓN PRECIO VS SENTIMIENTO (DOBLE EJE) - NUEVO
    # ─────────────────────────────────────────────────────────────────────────
    ax3 = plt.subplot(3, 2, 3)
    
    if df_sentimiento_diario is not None and not df_sentimiento_diario.empty:
        # Filtrar últimos 60 días para claridad
        fecha_corte = datetime.now() - timedelta(days=60)
        df_s_reciente = df_sentimiento_diario[df_sentimiento_diario['fecha'] >= fecha_corte]
        df_p_reciente = df_wti[df_wti['fecha'] >= fecha_corte]
        
        # Eje izquierdo: Precio
        color_p = 'tab:blue'
        ax3.set_ylabel('Precio WTI ($)', color=color_p, fontweight='bold')
        ax3.plot(df_p_reciente['fecha'], df_p_reciente['precio'], color=color_p, linewidth=2, label='Precio WTI')
        ax3.tick_params(axis='y', labelcolor=color_p)
        
        # Eje derecho: Sentimiento
        ax3_b = ax3.twinx()
        color_s = 'tab:red'
        ax3_b.set_ylabel('Sentimiento (Rolling 7d)', color=color_s, fontweight='bold')
        ax3_b.plot(df_s_reciente['fecha'], df_s_reciente['rolling_7d'], color=color_s, linestyle='--', linewidth=2, label='Sentimiento')
        ax3_b.tick_params(axis='y', labelcolor=color_s)
        ax3_b.axhline(0, color='gray', linestyle=':', alpha=0.5)
        
        ax3.set_title('Correlación: Precio vs Sentimiento (60d)', fontsize=11, fontweight='bold')
    else:
        ax3.text(0.5, 0.5, "Insuficientes datos históricos\npara correlación", ha='center', va='center')

    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 4: Termómetro de Riesgo
    # ─────────────────────────────────────────────────────────────────────────
    ax4 = plt.subplot(3, 2, 4)
    ax4.axis('off')
    riesgo_colores = {'BAJO': 'blue', 'MEDIO': 'green', 'MEDIO-ALTO': 'yellow', 'ALTO': 'red'}
    riesgo_valores = {'BAJO': 0.25, 'MEDIO': 0.5, 'MEDIO-ALTO': 0.75, 'ALTO': 1.0}
    nivel = riesgo_valores.get(recomendacion['riesgo'], 0.5)
    color = riesgo_colores.get(recomendacion['riesgo'], 'gray')
    
    ax4.add_patch(Rectangle((0.1, 0.4), 0.8, 0.2, facecolor='lightgray', edgecolor='black'))
    ax4.add_patch(Rectangle((0.1, 0.4), 0.8 * nivel, 0.2, facecolor=color, edgecolor='black', alpha=0.8))
    ax4.text(0.5, 0.7, 'NIVEL DE RIESGO', ha='center', fontsize=12, fontweight='bold')
    ax4.text(0.5, 0.5, recomendacion['riesgo'], ha='center', va='center', fontsize=14, fontweight='bold', color='white', bbox=dict(boxstyle='round', facecolor='black', alpha=0.6))
    ax4.set_xlim(0, 1); ax4.set_ylim(0, 1)

    # ─────────────────────────────────────────────────────────────────────────
    # GRÁFICO 5: Recomendación y Razones
    # ─────────────────────────────────────────────────────────────────────────
    ax5 = plt.subplot(3, 1, 3) # Ocupa todo el ancho abajo
    ax5.axis('off')
    
    # Título grande
    ax5.text(0.5, 0.9, f"{recomendacion['accion_icono']} {recomendacion['accion']}", ha='center', fontsize=20, fontweight='bold', bbox=dict(boxstyle='round', facecolor=recomendacion['color_riesgo'], alpha=0.3))
    
    # Razones (2 columnas)
    ax5.text(0.05, 0.7, "RAZONES PRINCIPALES:", fontsize=12, fontweight='bold')
    y = 0.6
    for razon in recomendacion['razones'][:3]:
        ax5.text(0.05, y, razon, fontsize=10); y -= 0.12
        
    ax5.text(0.55, 0.7, "NOTICIAS CLAVE:", fontsize=12, fontweight='bold')
    y = 0.6
    for n in noticias[:3]:
        c = 'green' if n['tipo']=='POSITIVA' else 'red' if n['tipo']=='NEGATIVA' else 'black'
        ax5.text(0.55, y, f"• {n['texto'][:60]}...", fontsize=9, color=c); y -= 0.12

    plt.tight_layout()
    ruta = f"{GRAFICAS_DIR}/dashboard_recomendacion.png"
    plt.savefig(ruta, dpi=300, bbox_inches='tight')
    print(f"  ✓ Dashboard guardado: {ruta}")
    plt.close()

def generar_graficos_adicionales(df_wti, df_sentimiento_diario):
    """
    Genera los 3 gráficos adicionales solicitados por el usuario.
    1. Sentimiento vs Precio (Detallado)
    2. Heatmap de Sentimiento
    3. Señal del Sistema en el tiempo
    """
    print("\n[6.2] Generando gráficos avanzados adicionales...")
    
    if df_sentimiento_diario is None or df_sentimiento_diario.empty:
        print("  ⚠️ No hay datos de sentimiento para gráficos adicionales.")
        return

    # Preparar datos fusionados
    df_merge = pd.merge(df_wti, df_sentimiento_diario, on='fecha', how='inner')
    df_merge = df_merge.sort_values('fecha')
    
    # ─────────────────────────────────────────────────────────────────────────
    # 1. SENTIMIENTO VS PRECIO (DOBLE EJE DETALLADO)
    # ─────────────────────────────────────────────────────────────────────────
    plt.figure(figsize=(12, 6))
    ax1 = plt.gca()
    
    # Precio
    ax1.plot(df_merge['fecha'], df_merge['precio'], color='#2c3e50', linewidth=2, label='Precio WTI')
    ax1.set_ylabel('Precio WTI ($)', color='#2c3e50', fontweight='bold')
    ax1.tick_params(axis='y', labelcolor='#2c3e50')
    
    # Sentimiento
    ax2 = ax1.twinx()
    # Rellenar área bajo la curva de sentimiento
    ax2.fill_between(df_merge['fecha'], df_merge['rolling_7d'], 0, where=(df_merge['rolling_7d']>=0), color='green', alpha=0.3, interpolate=True)
    ax2.fill_between(df_merge['fecha'], df_merge['rolling_7d'], 0, where=(df_merge['rolling_7d']<0), color='red', alpha=0.3, interpolate=True)
    ax2.plot(df_merge['fecha'], df_merge['rolling_7d'], color='#e74c3c', linewidth=1.5, linestyle='--', label='Sentimiento (7d)')
    ax2.set_ylabel('Score Sentimiento', color='#e74c3c', fontweight='bold')
    ax2.tick_params(axis='y', labelcolor='#e74c3c')
    
    plt.title('Dinámica Precio WTI vs Sentimiento de Noticias', fontsize=14, fontweight='bold')
    
    # Líneas de correlación visual
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    ruta1 = f"{GRAFICAS_DIR}/1_precio_vs_sentimiento.png"
    plt.savefig(ruta1, dpi=300)
    print(f"  ✓ Gráfico 1 guardado: {ruta1}")
    plt.close()
    
    # ─────────────────────────────────────────────────────────────────────────
    # 2. HEATMAP DE SENTIMIENTO HISTÓRICO
    # ─────────────────────────────────────────────────────────────────────────
    try:
        df_heat = df_sentimiento_diario.copy()
        df_heat['year'] = df_heat['fecha'].dt.year
        df_heat['month'] = df_heat['fecha'].dt.month
        df_heat['day'] = df_heat['fecha'].dt.day
        
        # Pivot table: Mes vs Día (del año actual/reciente)
        pivot_table = df_heat.pivot_table(index='month', columns='day', values='rolling_7d', aggfunc='mean')
        
        plt.figure(figsize=(12, 5))
        sns.heatmap(pivot_table, cmap='RdYlGn', center=0, annot=False, cbar_kws={'label': 'Sentimiento'})
        plt.title('Mapa de Calor: Intensidad del Sentimiento Diario', fontsize=14, fontweight='bold')
        plt.ylabel('Mes')
        plt.xlabel('Día del Mes')
        plt.tight_layout()
        
        ruta2 = f"{GRAFICAS_DIR}/2_heatmap_sentimiento.png"
        plt.savefig(ruta2, dpi=300)
        print(f"  ✓ Gráfico 2 guardado: {ruta2}")
    except Exception as e:
        print(f"  ⚠️ No se pudo generar heatmap: {e}")
    plt.close()
    
    # ─────────────────────────────────────────────────────────────────────────
    # 3. SEÑAL DEL SISTEMA A TRAVÉS DEL TIEMPO (RECONSTRUCCIÓN)
    # ─────────────────────────────────────────────────────────────────────────
    # Reconstruimos un "Score Histórico" aproximado
    # Score = 0.5 * Tecnico + 0.5 * Sentimiento (Ignoramos predicción histórica por complejidad)
    
    df_merge['rsi_norm'] = df_merge['RSI'] / 100
    df_merge['sent_norm'] = (df_merge['rolling_7d'] + 1) / 2
    
    # Score aproximado histórico
    df_merge['score_hist'] = 0.5 * df_merge['rsi_norm'] + 0.5 * df_merge['sent_norm']
    
    plt.figure(figsize=(12, 6))
    
    # Zonas de decisión
    plt.axhspan(0.65, 1.0, color='green', alpha=0.1, label='Zona Compra Fuerte')
    plt.axhspan(0.55, 0.65, color='lightgreen', alpha=0.1, label='Zona Compra')
    plt.axhspan(0.45, 0.55, color='yellow', alpha=0.1, label='Zona Mantener')
    plt.axhspan(0.35, 0.45, color='orange', alpha=0.1, label='Zona Venta')
    plt.axhspan(0.0, 0.35, color='red', alpha=0.1, label='Zona Venta Fuerte')
    
    plt.plot(df_merge['fecha'], df_merge['score_hist'], color='purple', linewidth=2, label='Score del Sistema')
    plt.scatter(df_merge['fecha'], df_merge['score_hist'], c=df_merge['score_hist'], cmap='RdYlGn', zorder=5)
    
    plt.title('Evolución Histórica de la Señal del Sistema', fontsize=14, fontweight='bold')
    plt.ylabel('Score Integrado (0-1)')
    plt.grid(True, alpha=0.3)
    plt.legend(loc='lower left')
    
    ruta3 = f"{GRAFICAS_DIR}/3_senal_sistema_historica.png"
    plt.savefig(ruta3, dpi=300)
    print(f"  ✓ Gráfico 3 guardado: {ruta3}")
    plt.close()

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 7: REPORTE EN TERMINAL
# ══════════════════════════════════════════════════════════════════════════════

def imprimir_reporte_terminal(df_wti, df_brent, señal_tecnica, metricas, recomendacion, noticias):
    """
    Imprime reporte profesional en terminal
    """
    print("\n\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*25 + "RECOMENDACIÓN DEL DÍA" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\n📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # RECOMENDACIÓN
    print("\n" + "─"*80)
    print(f"  {recomendacion['accion_icono']}  ACCIÓN RECOMENDADA: {recomendacion['accion']}")
    print("─"*80)
    
    print(f"\n📊 Score Integrado: {recomendacion['score']:.3f}")
    print(f"🎯 Nivel de Confianza: {recomendacion['confianza']:.0f}%")
    print(f"⚠️  Riesgo Actual: {recomendacion['riesgo']}")
    
    # RAZONES
    print(f"\n💡 RAZONES DE LA DECISIÓN:")
    for i, razon in enumerate(recomendacion['razones'], 1):
        print(f"  {i}. {razon}")
    
    # DATOS WTI
    print(f"\n🛢️  WTI (West Texas Intermediate):")
    print(f"  Precio actual: ${df_wti['precio'].iloc[-1]:.2f}/barril")
    print(f"  Predicción {DIAS_PREDICCION} días: ${metricas['precio_predicho']:.2f}")
    print(f"  Cambio esperado: {metricas['cambio_porcentual']:+.2f}%")
    
    # COMPARACIÓN BRENT
    print(f"\n🌍 Comparación WTI vs. Brent:")
    spread = df_brent['precio'].iloc[-1] - df_wti['precio'].iloc[-1]
    print(f"  Brent: ${df_brent['precio'].iloc[-1]:.2f}/barril")
    print(f"  Spread Brent-WTI: ${spread:+.2f}")
    
    # ANÁLISIS TÉCNICO
    print(f"\n📈 Análisis Técnico:")
    print(f"  Tendencia: {señal_tecnica['tendencia']}")
    print(f"  RSI (14): {señal_tecnica['rsi']:.1f} ({señal_tecnica['rsi_señal']})")
    print(f"  Soporte: ${señal_tecnica['soporte']:.2f}")
    print(f"  Resistencia: ${señal_tecnica['resistencia']:.2f}")
    
    # NOTICIAS
    print(f"\n📰 Noticias Relevantes:")
    for i, noticia in enumerate(noticias[:3], 1):
        icono = "🟢" if noticia['tipo'] == "POSITIVA" else "🔴" if noticia['tipo'] == "NEGATIVA" else "ℹ️"
        print(f"  {icono} {noticia['texto']}")
        if noticia['score'] != 0:
            print(f"     Score: {noticia['score']:+.2f}")
    
    # GRÁFICAS Y ARCHIVOS
    print(f"\n📂 UBICACIÓN DE ARCHIVOS GENERADOS:")
    print(f"  1. Base de Noticias:   {os.path.abspath('base_datos_csv/noticias_historico.csv')}")
    print(f"  2. Dashboard Visual:   {os.path.abspath(f'{GRAFICAS_DIR}/dashboard_recomendacion.png')}")
    print(f"  3. Gráfico Precio-Sent:{os.path.abspath(f'{GRAFICAS_DIR}/1_precio_vs_sentimiento.png')}")
    print(f"  4. Heatmap:            {os.path.abspath(f'{GRAFICAS_DIR}/2_heatmap_sentimiento.png')}")
    print(f"  5. Señal Histórica:    {os.path.abspath(f'{GRAFICAS_DIR}/3_senal_sistema_historica.png')}")
    
    print("\n" + "="*80 + "\n")

    # ABRIR GUI VISUAL (IMAGEN)
    try:
        print("🖥️  Abriendo visualización gráfica...")
        if sys.platform == 'win32':
            os.startfile(os.path.abspath(f"{GRAFICAS_DIR}/dashboard_recomendacion.png"))
        else:
            # Linux/Mac (opcional, por si acaso)
            import subprocess
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, os.path.abspath(f"{GRAFICAS_DIR}/dashboard_recomendacion.png")])
    except Exception as e:
        print(f"  ⚠️ No se pudo abrir la imagen automáticamente: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# MAIN - EJECUCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Ejecuta el sistema completo de recomendación
    """
    tiempo_inicio = time.time()
    
    # 1. Descargar datos precios
    df_wti, df_brent = descargar_datos_petroleo()
    
    # 2. Análisis técnico
    df_wti, señal_tecnica = calcular_indicadores_tecnicos(df_wti)
    
    # 3. Predicción
    forecast, metricas_prediccion = generar_prediccion(df_wti, dias=DIAS_PREDICCION)
    
    # 4. Sentimiento (NUEVO: Pasa df_wti para correlación)
    sentimiento_score, noticias_relevantes, df_sentimiento_diario = analizar_sentimiento_mercado(df_wti)
    
    # 5. Generar recomendación
    recomendacion = generar_recomendacion(señal_tecnica, metricas_prediccion, sentimiento_score)
    
    # 6. Visualizaciones (NUEVO: Pasa df_sentimiento_diario)
    generar_dashboard(df_wti, df_brent, forecast, señal_tecnica, recomendacion, noticias_relevantes, df_sentimiento_diario)
    
    # 6.2 Gráficos Adicionales
    generar_graficos_adicionales(df_wti, df_sentimiento_diario)
    
    # 7. Reporte terminal
    imprimir_reporte_terminal(df_wti, df_brent, señal_tecnica, metricas_prediccion, recomendacion, noticias_relevantes)
    
    tiempo_total = time.time() - tiempo_inicio
    print(f"⏱️  Tiempo de ejecución: {tiempo_total:.1f} segundos")
    print(f"✅ Sistema ejecutado exitosamente\n")

if __name__ == "__main__":
    main()
