"""
Script Mejorado: Descarga de Noticias REALES sobre Petróleo
Fuentes: Google News RSS, Yahoo Finance, Reddit
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re

print("=" * 70)
print("DESCARGA DE NOTICIAS REALES SOBRE PETRÓLEO")
print("=" * 70)

# ========== FUNCIÓN 1: Google News RSS ==========
def obtener_google_news(tema="oil prices", max_noticias=30):
    """Descarga noticias de Google News RSS"""
    print(f"\n[1/3] Descargando noticias de Google News (tema: {tema})...")
    
    try:
        # URL de Google News RSS
        url = f"https://news.google.com/rss/search?q={tema.replace(' ', '+')}&hl=en-US&gl=US&ceid=US:en"
        
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'xml')
        
        items = soup.find_all('item')[:max_noticias]
        
        noticias = []
        for i, item in enumerate(items, 1):
            titulo = item.find('title').text if item.find('title') else "Sin título"
            fecha_str = item.find('pubDate').text if item.find('pubDate') else None
            link = item.find('link').text if item.find('link') else ""
            
            # Parsear fecha
            try:
                # Formato: "Mon, 01 Dec 2024 12:00:00 GMT"
                fecha = datetime.strptime(fecha_str, '%a, %d %b %Y %H:%M:%S %Z') if fecha_str else datetime.now()
            except:
                fecha = datetime.now()
            
            noticias.append({
                'noticia_id': f"GN{i:04d}",
                'fuente': 'Google News',
                'fecha': fecha.strftime('%Y-%m-%d'),
                'titulo': titulo,
                'link': link
            })
        
        print(f"  ✓ Descargadas {len(noticias)} noticias de Google News")
        return noticias
    
    except Exception as e:
        print(f"  ⚠️ Error al descargar Google News: {e}")
        return []

# ========== FUNCIÓN 2: Yahoo Finance News ==========
def obtener_yahoo_finance_news(ticker="CL=F", max_noticias=20):
    """Descarga noticias de Yahoo Finance para WTI (CL=F)"""
    print(f"\n[2/3] Descargando noticias de Yahoo Finance (ticker: {ticker})...")
    
    try:
        import yfinance as yf
        
        # Obtener objeto ticker
        oil = yf.Ticker(ticker)
        
        # Obtener noticias (si están disponibles)
        try:
            news = oil.news[:max_noticias]
        except:
            news = []
        
        noticias = []
        for i, item in enumerate(news, 1):
            titulo = item.get('title', 'Sin título')
            fecha_timestamp = item.get('providerPublishTime', time.time())
            fecha = datetime.fromtimestamp(fecha_timestamp)
            link = item.get('link', '')
            
            noticias.append({
                'noticia_id': f"YF{i:04d}",
                'fuente': 'Yahoo Finance',
                'fecha': fecha.strftime('%Y-%m-%d'),
                'titulo': titulo,
                'link': link
            })
        
        print(f"  ✓ Descargadas {len(noticias)} noticias de Yahoo Finance")
        return noticias
    
    except Exception as e:
        print(f"  ⚠️ Error al descargar Yahoo Finance: {e}")
        return []

# ========== FUNCIÓN 3: Reddit (opcional) ==========
def obtener_reddit_posts(subreddit="oil", max_posts=20):
    """Descarga posts de Reddit sobre petróleo (requiere API key)"""
    print(f"\n[3/3] Intentando descargar posts de Reddit (r/{subreddit})...")
    
    try:
        # Usar Reddit sin autenticación (limitado)
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={max_posts}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        
        posts = data['data']['children']
        
        noticias = []
        for i, post in enumerate(posts, 1):
            post_data = post['data']
            titulo = post_data.get('title', 'Sin título')
            fecha_timestamp = post_data.get('created_utc', time.time())
            fecha = datetime.fromtimestamp(fecha_timestamp)
            link = f"https://reddit.com{post_data.get('permalink', '')}"
            
            noticias.append({
                'noticia_id': f"RD{i:04d}",
                'fuente': 'Reddit',
                'fecha': fecha.strftime('%Y-%m-%d'),
                'titulo': titulo,
                'link': link
            })
        
        print(f"  ✓ Descargados {len(noticias)} posts de Reddit")
        return noticias
    
    except Exception as e:
        print(f"  ⚠️ Error al descargar Reddit: {e}")
        print("     (Esto es normal si Reddit bloquea requests sin API key)")
        return []

# ========== FUNCIÓN 4: Limpiar y Filtrar ==========
def filtrar_noticias_relevantes(noticias):
    """Filtra noticias que realmente hablen de petróleo/oil"""
    keywords = ['oil', 'crude', 'wti', 'brent', 'opec', 'petroleum', 'energy', 
                'barrel', 'price', 'production', 'inventory', 'petrol']
    
    noticias_filtradas = []
    for noticia in noticias:
        titulo_lower = noticia['titulo'].lower()
        # Verificar si contiene al menos una keyword
        if any(keyword in titulo_lower for keyword in keywords):
            noticias_filtradas.append(noticia)
    
    return noticias_filtradas

# ========== EJECUCIÓN PRINCIPAL ==========
if __name__ == "__main__":
    
    todas_noticias = []
    
    # Descargar de múltiples fuentes
    noticias_google = obtener_google_news("oil prices WTI", max_noticias=30)
    noticias_yahoo = obtener_yahoo_finance_news("CL=F", max_noticias=20)
    noticias_reddit = obtener_reddit_posts("oil", max_posts=15)
    
    # Combinar todas
    todas_noticias.extend(noticias_google)
    todas_noticias.extend(noticias_yahoo)
    todas_noticias.extend(noticias_reddit)
    
    # Filtrar relevantes
    print(f"\n[4/4] Filtrando noticias relevantes...")
    noticias_filtradas = filtrar_noticias_relevantes(todas_noticias)
    print(f"  ✓ {len(noticias_filtradas)}/{len(todas_noticias)} noticias son relevantes")
    
    # Eliminar duplicados por título similar
    noticias_unicas = []
    titulos_vistos = set()
    
    for noticia in noticias_filtradas:
        # Crear firma simplificada del título
        titulo_limpio = re.sub(r'[^a-z0-9\s]', '', noticia['titulo'].lower())
        palabras = set(titulo_limpio.split()[:5])  # Primeras 5 palabras
        firma = ' '.join(sorted(palabras))
        
        if firma not in titulos_vistos:
            titulos_vistos.add(firma)
            noticias_unicas.append(noticia)
    
    print(f"  ✓ {len(noticias_unicas)} noticias únicas (sin duplicados)")
    
    # Convertir a DataFrame
    df_noticias = pd.DataFrame(noticias_unicas)
    
    # Ordenar por fecha (más recientes primero)
    df_noticias['fecha'] = pd.to_datetime(df_noticias['fecha'])
    df_noticias = df_noticias.sort_values('fecha', ascending=False)
    
    # Resetear índice
    df_noticias = df_noticias.reset_index(drop=True)
    df_noticias['noticia_id'] = [f"NOT{i:04d}" for i in range(len(df_noticias))]
    
    # Guardar
    import os
    os.makedirs('base_datos_csv', exist_ok=True)
    
    df_noticias.to_csv('base_datos_csv/noticias_reales.csv', index=False, encoding='utf-8')
    
    # Mostrar resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE DESCARGA")
    print("=" * 70)
    print(f"\nTotal de noticias descargadas: {len(noticias_unicas)}")
    print(f"Archivo guardado: base_datos_csv/noticias_reales.csv")
    
    print(f"\nDistribución por fuente:")
    print(df_noticias['fuente'].value_counts().to_string())
    
    print(f"\nÚltimas 5 noticias:")
    for i, row in df_noticias.head(5).iterrows():
        print(f"\n{i+1}. [{row['fuente']}] {row['fecha'].strftime('%Y-%m-%d')}")
        print(f"   {row['titulo'][:80]}...")
    
    print("\n" + "=" * 70)
    print("✅ Noticias REALES descargadas exitosamente")
    print("   Ahora ejecuta: python 3_analisis_sentimiento_real.py")
    print("=" * 70)
