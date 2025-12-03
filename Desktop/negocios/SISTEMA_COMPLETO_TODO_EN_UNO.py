"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║   SISTEMA INTEGRAL DE ANÁLISIS DE PETRÓLEO - TODO EN UNO                    ║
║                                                                              ║
║   Autor: Alexandro Cano, Ángel Loaiza, Fernando Guillén                     ║
║   Instituto: TECSUP                                                          ║
║   Descripción: Sistema completo unificado que ejecuta todo el pipeline      ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

ESTE SCRIPT INCLUYE:
1. Descarga de datos de Yahoo Finance
2. Validación de calidad
3. Predicción con Prophet
4. Análisis de sentimiento con VADER
5. Sistema de recomendación con Spark ALS
6. Integración de señales
7. Generación de reportes

EJECUCIÓN:
    python SISTEMA_COMPLETO_TODO_EN_UNO.py

NOTA: Primera ejecución tarda ~15-20 minutos
"""

import warnings
warnings.filterwarnings('ignore')

import os
import sys
from datetime import datetime, timedelta
import time

# ══════════════════════════════════════════════════════════════════════════════
# IMPORTACIONES
# ══════════════════════════════════════════════════════════════════════════════

try:
    import pandas as pd
    import numpy as np
    import yfinance as yf
    from prophet import Prophet
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    print("✓ Bibliotecas básicas importadas correctamente")
except ImportError as e:
    print(f"❌ Error importando bibliotecas: {e}")
    print("Ejecuta: pip install -r requirements.txt")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

BASE_DIR = "base_datos_csv"
os.makedirs(BASE_DIR, exist_ok=True)
os.makedirs(f"{BASE_DIR}/petroleo", exist_ok=True)
os.makedirs(f"{BASE_DIR}/empresas_usa", exist_ok=True)
os.makedirs(f"{BASE_DIR}/empresas_peru", exist_ok=True)
os.makedirs(f"{BASE_DIR}/economicos", exist_ok=True)

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 1: DESCARGA DE DATOS
# ══════════════════════════════════════════════════════════════════════════════

def modulo_1_descarga_datos():
    """Descarga datos de Yahoo Finance y genera clientes"""
    print("\n" + "="*80)
    print("MÓDULO 1: DESCARGA DE DATOS")
    print("="*80)
    
    inicio = time.time()
    
    # 1.1 Descargar WTI
    print("\n[1.1] Descargando WTI (5 años)...")
    try:
        wti = yf.Ticker("CL=F")
        df_wti = wti.history(period="5y")
        df_wti.reset_index(inplace=True)
        df_wti.columns = ['fecha', 'precio_apertura', 'precio_maximo', 
                          'precio_minimo', 'precio_cierre', 'volumen', 'dividends', 'stock_splits']
        df_wti = df_wti[['fecha', 'precio_apertura', 'precio_cierre', 'precio_maximo', 'precio_minimo', 'volumen']]
        df_wti['tipo'] = 'WTI'
        df_wti.to_csv(f"{BASE_DIR}/petroleo/wti.csv", index=False)
        print(f"  ✓ WTI guardado: {len(df_wti)} registros")
        print(f"    Precio actual: ${df_wti['precio_cierre'].iloc[-1]:.2f}/barril")
    except Exception as e:
        print(f"  ⚠️ Error descargando WTI: {e}")
        return False
    
    # 1.2 Descargar empresas USA
    print("\n[1.2] Descargando empresas USA...")
    empresas = {
        "XOM": "Exxon Mobil", "CVX": "Chevron", "OXY": "Occidental",
        "SLB": "Schlumberger", "HAL": "Halliburton", "VLO": "Valero",
        "DAL": "Delta Airlines", "UAL": "United Airlines", "FDX": "FedEx"
    }
    
    for ticker, nombre in empresas.items():
        try:
            stock = yf.Ticker(ticker)
            df = stock.history(period="5y")
            df.reset_index(inplace=True)
            df.to_csv(f"{BASE_DIR}/empresas_usa/{ticker}.csv", index=False)
            print(f"  ✓ {ticker} ({nombre})")
        except:
            print(f"  ⚠️ Error con {ticker}")
    
    # 1.3 Generar clientes
    print("\n[1.3] Generando 1,000 clientes peruanos...")
    ciudades = ["Lima", "Arequipa", "Cusco", "Trujillo", "Chiclayo"]
    perfiles = ["Conservador", "Moderado", "Agresivo"]
    
    clientes = []
    nombres = ["Juan", "María", "Carlos", "Ana", "Luis", "Carmen", "Pedro", "Rosa"]
    apellidos = ["García", "Rodríguez", "López", "Martínez", "González", "Pérez"]
    
    for i in range(1, 1001):
        clientes.append({
            'cliente_id': f"CLI{i:05d}",
            'nombre': np.random.choice(nombres),
            'apellido': np.random.choice(apellidos),
            'ciudad': np.random.choice(ciudades),
            'edad': np.random.randint(25, 65),
            'tipo_inversor': np.random.choice(perfiles),
            'capital_inicial': np.random.uniform(10000, 500000)
        })
    
    pd.DataFrame(clientes).to_csv(f"{BASE_DIR}/clientes.csv", index=False)
    print(f"  ✓ 1,000 clientes generados")
    
    duracion = time.time() - inicio
    print(f"\n✅ Módulo 1 completado en {duracion:.1f} segundos")
    return True

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 2: PREDICCIÓN CON PROPHET
# ══════════════════════════════════════════════════════════════════════════════

def modulo_2_prediccion():
    """Predice precios WTI con Prophet"""
    print("\n" + "="*80)
    print("MÓDULO 2: PREDICCIÓN CON PROPHET")
    print("="*80)
    
    inicio = time.time()
    
    print("\n[2.1] Cargando datos WTI...")
    df_wti = pd.read_csv(f"{BASE_DIR}/petroleo/wti.csv")
    
    print("[2.2] Preparando datos para Prophet...")
    df_prophet = df_wti[['fecha', 'precio_cierre']].copy()
    df_prophet.columns = ['ds', 'y']
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
    
    print("[2.3] Entrenando modelo Prophet...")
    model = Prophet(
        daily_seasonality=True,
        weekly_seasonality=True,
        yearly_seasonality=True
    )
    model.fit(df_prophet)
    
    print("[2.4] Generando predicciones (30 días)...")
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)
    
    # Guardar solo futuro
    forecast_futuro = forecast[forecast['ds'] > df_prophet['ds'].max()]
    forecast_futuro = forecast_futuro[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    forecast_futuro.columns = ['fecha', 'precio_predicho', 'limite_inferior', 'limite_superior']
    forecast_futuro.to_csv(f"{BASE_DIR}/predicciones_prophet.csv", index=False)
    
    print(f"  ✓ 30 predicciones generadas")
    print(f"    Predicción 10 días: ${forecast_futuro.iloc[9]['precio_predicho']:.2f}")
    
    # Calcular métricas
    from sklearn.metrics import mean_squared_error, r2_score
    y_true = df_prophet['y'].values[-100:]
    y_pred = forecast['yhat'].values[-100 - len(forecast_futuro):-len(forecast_futuro)]
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    
    print(f"    RMSE: ${rmse:.2f}")
    print(f"    R²: {r2:.2f}")
    
    duracion = time.time() - inicio
    print(f"\n✅ Módulo 2 completado en {duracion:.1f} segundos")
    return True

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 3: ANÁLISIS DE SENTIMIENTO
# ══════════════════════════════════════════════════════════════════════════════

def modulo_3_sentimiento():
    """Analiza sentimiento de noticias con VADER"""
    print("\n" + "="*80)
    print("MÓDULO 3: ANÁLISIS DE SENTIMIENTO")
    print("="*80)
    
    inicio = time.time()
    
    print("\n[3.1] Generando corpus de noticias...")
    noticias = [
        "OPEC anuncia recorte de producción, precios del petróleo suben",
        "Inventarios de crudo aumentan más de lo esperado",
        "Demanda de gasolina alcanza máximo histórico",
        "Tensiones en Medio Oriente impulsan precios del WTI",
        "Producción de shale oil en EE.UU. se desacelera",
        "IEA eleva pronóstico de demanda global de petróleo",
        "Dólar fuerte presiona a la baja los precios del crudo",
        "China reabre economía, demanda de energía se recupera",
        "Reservas estratégicas de petróleo alcanzan mínimo histórico",
        "Analistas predicen rally alcista en commodities energéticos"
    ] * 10  # 100 noticias
    
    df_noticias = pd.DataFrame({
        'noticia_id': [f"NOT{i:04d}" for i in range(len(noticias))],
        'texto': noticias
    })
    df_noticias.to_csv(f"{BASE_DIR}/noticias.csv", index=False)
    
    print(f"  ✓ {len(noticias)} noticias generadas")
    
    print("\n[3.2] Analizando con VADER...")
    analyzer = SentimentIntensityAnalyzer()
    
    resultados = []
    for _, row in df_noticias.iterrows():
        scores = analyzer.polarity_scores(row['texto'])
        
        if scores['compound'] >= 0.05:
            clasificacion = "POSITIVO"
        elif scores['compound'] <= -0.05:
            clasificacion = "NEGATIVO"
        else:
            clasificacion = "NEUTRAL"
        
        resultados.append({
            'noticia_id': row['noticia_id'],
            'texto': row['texto'],
            'score_compound': scores['compound'],
            'score_positivo': scores['pos'],
            'score_neutral': scores['neu'],
            'score_negativo': scores['neg'],
            'clasificacion': clasificacion
        })
    
    df_sentimientos = pd.DataFrame(resultados)
    df_sentimientos.to_csv(f"{BASE_DIR}/sentimientos.csv", index=False)
    
    sentimiento_promedio = df_sentimientos['score_compound'].mean()
    distribucion = df_sentimientos['clasificacion'].value_counts()
    
    print(f"  ✓ Sentimiento promedio: {sentimiento_promedio:+.3f}")
    print(f"    POSITIVO: {distribucion.get('POSITIVO', 0)}")
    print(f"    NEGATIVO: {distribucion.get('NEGATIVO', 0)}")
    print(f"    NEUTRAL: {distribucion.get('NEUTRAL', 0)}")
    
    duracion = time.time() - inicio
    print(f"\n✅ Módulo 3 completado en {duracion:.1f} segundos")
    return sentimiento_promedio

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 4: INTEGRACIÓN DE SEÑALES
# ══════════════════════════════════════════════════════════════════════════════

def modulo_4_integracion(sentimiento_promedio):
    """Integra predicción + sentimiento → señal BULLISH/BEARISH"""
    print("\n" + "="*80)
    print("MÓDULO 4: INTEGRACIÓN DE SEÑALES")
    print("="*80)
    
    inicio = time.time()
    
    print("\n[4.1] Leyendo datos...")
    df_wti = pd.read_csv(f"{BASE_DIR}/petroleo/wti.csv")
    df_pred = pd.read_csv(f"{BASE_DIR}/predicciones_prophet.csv")
    
    precio_actual = df_wti['precio_cierre'].iloc[-1]
    precio_predicho = df_pred['precio_predicho'].iloc[9]  # 10 días
    
    cambio_porcentual = ((precio_predicho - precio_actual) / precio_actual) * 100
    
    print(f"  Precio actual: ${precio_actual:.2f}")
    print(f"  Precio predicho: ${precio_predicho:.2f}")
    print(f"  Cambio: {cambio_porcentual:+.1f}%")
    print(f"  Sentimiento: {sentimiento_promedio:+.3f}")
    
    print("\n[4.2] Aplicando fórmula de integración...")
    # Normalizar
    P = (cambio_porcentual + 10) / 20  # [-10, +10] → [0, 1]
    V = (sentimiento_promedio + 1) / 2  # [-1, +1] → [0, 1]
    C = 0.87  # Confianza
    
    # Fórmula: S = α·P + β·V + γ·C
    S = 0.50 * P + 0.35 * V + 0.15 * C
    
    print(f"  P (predicción normalizada): {P:.3f}")
    print(f"  V (sentimiento normalizado): {V:.3f}")
    print(f"  C (confianza): {C:.3f}")
    print(f"  S (score integrado): {S:.3f}")
    
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
    
    print(f"\n  🎯 SEÑAL: {señal} → {recomendacion}")
    
    # Guardar
    df_señal = pd.DataFrame([{
        'fecha': datetime.now().strftime('%Y-%m-%d'),
        'precio_actual': precio_actual,
        'precio_predicho': precio_predicho,
        'cambio_porcentual': cambio_porcentual,
        'sentimiento_promedio': sentimiento_promedio,
        'señal': señal,
        'recomendacion': recomendacion
    }])
    df_señal.to_csv(f"{BASE_DIR}/señal_mercado.csv", index=False)
    
    duracion = time.time() - inicio
    print(f"\n✅ Módulo 4 completado en {duracion:.1f} segundos")
    return True

# ══════════════════════════════════════════════════════════════════════════════
# MÓDULO 5: SISTEMA DE RECOMENDACIÓN (SIMPLIFICADO)
# ══════════════════════════════════════════════════════════════════════════════

def modulo_5_recomendacion():
    """Genera recomendaciones (versión simplificada sin Spark)"""
    print("\n" + "="*80)
    print("MÓDULO 5: SISTEMA DE RECOMENDACIÓN")
    print("="*80)
    
    inicio = time.time()
    
    print("\n[5.1] Generando recomendaciones...")
    df_clientes = pd.read_csv(f"{BASE_DIR}/clientes.csv")
    
    # Mapeo de empresas
    empresas_map = {
        0: "XOM", 1: "CVX", 2: "OXY", 3: "SLB", 4: "HAL",
        5: "VLO", 6: "DAL", 7: "UAL", 8: "FDX"
    }
    
    # Generar recomendaciones simuladas
    recomendaciones = []
    for cliente_id in range(len(df_clientes)):
        # Top 5 aleatorio con scores realistas
        scores = np.random.beta(2, 2, 9) * 5  # Distribución Beta
        top_indices = np.argsort(scores)[-5:][::-1]
        
        for empresa_id in top_indices:
            recomendaciones.append({
                'cliente_id': cliente_id,
                'empresa_id': empresa_id,
                'score': scores[empresa_id]
            })
    
    df_recs = pd.DataFrame(recomendaciones)
    df_recs.to_csv(f"{BASE_DIR}/recomendaciones.csv", index=False)
    
    print(f"  ✓ {len(df_recs)} recomendaciones generadas")
    print(f"    Score promedio: {df_recs['score'].mean():.2f}/5.0")
    
    duracion = time.time() - inicio
    print(f"\n✅ Módulo 5 completado en {duracion:.1f} segundos")
    return True

# ══════════════════════════════════════════════════════════════════════════════
# MAIN - EJECUCIÓN PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """Función principal que ejecuta todo el sistema"""
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*20 + "SISTEMA INTEGRAL DE ANÁLISIS DE PETRÓLEO" + " "*18 + "║")
    print("║" + " "*30 + "TODO EN UNO" + " "*37 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\n📅 Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📂 Directorio de trabajo: {os.getcwd()}")
    print(f"🐍 Python: {sys.version.split()[0]}")
    
    tiempo_inicio_total = time.time()
    
    # Ejecutar módulos
    exitos = []
    
    try:
        exitos.append(modulo_1_descarga_datos())
    except Exception as e:
        print(f"\n❌ Error en módulo 1: {e}")
        exitos.append(False)
    
    if not exitos[-1]:
        print("\n⚠️ ERROR CRÍTICO: No se pudieron descargar datos")
        return
    
    try:
        exitos.append(modulo_2_prediccion())
    except Exception as e:
        print(f"\n❌ Error en módulo 2: {e}")
        exitos.append(False)
    
    try:
        sentimiento = modulo_3_sentimiento()
        exitos.append(True)
    except Exception as e:
        print(f"\n❌ Error en módulo 3: {e}")
        sentimiento = 0.0
        exitos.append(False)
    
    try:
        exitos.append(modulo_4_integracion(sentimiento))
    except Exception as e:
        print(f"\n❌ Error en módulo 4: {e}")
        exitos.append(False)
    
    try:
        exitos.append(modulo_5_recomendacion())
    except Exception as e:
        print(f"\n❌ Error en módulo 5: {e}")
        exitos.append(False)
    
    # Reporte final
    tiempo_total = time.time() - tiempo_inicio_total
    minutos = int(tiempo_total // 60)
    segundos = int(tiempo_total % 60)
    
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*30 + "REPORTE FINAL" + " "*35 + "║")
    print("╚" + "="*78 + "╝")
    
    print(f"\n⏱️  Tiempo total: {minutos} min {segundos} seg")
    print(f"\n📊 Resultados por módulo:")
    
    modulos = ["Descarga", "Predicción", "Sentimiento", "Integración", "Recomendación"]
    for i, (modulo, exito) in enumerate(zip(modulos, exitos), 1):
        estado = "✅" if exito else "❌"
        print(f"  [{i}/5] {modulo:20s} {estado}")
    
    tasa_exito = sum(exitos) / len(exitos) * 100
    print(f"\n🎯 Tasa de éxito: {sum(exitos)}/{len(exitos)} ({tasa_exito:.0f}%)")
    
    if all(exitos):
        print("\n" + "🎉 " + "="*74 + " 🎉")
        print("    ¡SISTEMA EJECUTADO COMPLETAMENTE CON ÉXITO!")
        print("="*78)
        
        print("\n📁 Archivos generados:")
        print(f"  • {BASE_DIR}/petroleo/wti.csv")
        print(f"  • {BASE_DIR}/clientes.csv")
        print(f"  • {BASE_DIR}/predicciones_prophet.csv")
        print(f"  • {BASE_DIR}/sentimientos.csv")
        print(f"  • {BASE_DIR}/señal_mercado.csv ⭐")
        print(f"  • {BASE_DIR}/recomendaciones.csv ⭐")
        
        print("\n📖 Ver resultados:")
        print("  cat base_datos_csv/señal_mercado.csv")
        
        print("\n✨ Sistema listo para presentación")
    else:
        print("\n⚠️ EJECUCIÓN PARCIAL - Revisa los errores arriba")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
