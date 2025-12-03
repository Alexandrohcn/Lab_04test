"""
INTEGRACIÓN DE ANÁLISIS DE RIESGO REGIONAL: PERÚ
Para agregar al Sistema de Recomendación de Petróleo

Este módulo propone cómo integrar la problemática identificada en Perú
como factor de riesgo en el sistema de recomendación.
"""

import pandas as pd
from datetime import datetime, timedelta

# ══════════════════════════════════════════════════════════════════════════════
# ÍNDICE DE RIESGO REGIONAL PERÚ
# ══════════════════════════════════════════════════════════════════════════════

def calcular_indice_riesgo_peru():
    """
    Calcula índice de riesgo basado en eventos documentados en Perú.
    
    FACTORES DE RIESGO:
    - Derrumbes en Carretera Interoceánica
    - Sabotajes al Oleoducto Norperuano
    - Crisis financiera Petroperú
    - Producción estancada
    
    RETORNA:
        risk_score: float [0, 1] donde 1 = máximo riesgo
        risk_level: str (BAJO/MEDIO/ALTO/CRÍTICO)
    """
    
    # Base de datos de incidentes 2025
    incidentes_infraestructura = {
        'derrumbes_carretera': [
            {'fecha': '2025-09-15', 'severidad': 0.8, 'ubicacion': 'Carabaya, Puno'},
            {'fecha': '2025-06-20', 'severidad': 0.9, 'ubicacion': 'Cusco, Tramo 2'},
            {'fecha': '2025-03-10', 'severidad': 1.0, 'ubicacion': 'Iñapari, Madre de Dios'}
        ],
        'sabotajes_onp': [
            {'fecha': '2025-05-15', 'tipo': 'manipulacion_grapa', 'severidad': 0.9},
            {'fecha': '2025-04-12', 'tipo': 'fuga_hidrocarburos', 'severidad': 0.8},
            {'fecha': '2025-03-08', 'tipo': 'perforacion_intencional', 'severidad': 0.9}
        ],
        'crisis_financiera': {
            'calificacion_credito': 'PERDIDA',  # 2022
            'deuda_talara': 6.5e9,  # $6.5 mil millones
            'crecimiento_proyectado_2025': 0.0  # 0% crecimiento
        }
    }
    
    # CÁLCULO: Ponderación de factores
    
    # 1. Factor de infraestructura vial (últimos 180 días)
    fecha_actual = datetime.now()
    fecha_limite = fecha_actual - timedelta(days=180)
    
    derrumbes_recientes = [
        d for d in incidentes_infraestructura['derrumbes_carretera']
        if datetime.strptime(d['fecha'], '%Y-%m-%d') >= fecha_limite
    ]
    
    peso_derrumbes = sum(d['severidad'] for d in derrumbes_recientes) / 3  # Normalizar
    peso_derrumbes = min(peso_derrumbes, 1.0)
    
    # 2. Factor de sabotaje ONP (últimos 90 días)
    fecha_limite_onp = fecha_actual - timedelta(days=90)
    
    sabotajes_recientes = [
        s for s in incidentes_infraestructura['sabotajes_onp']
        if datetime.strptime(s['fecha'], '%Y-%m-%d') >= fecha_limite_onp
    ]
    
    peso_sabotajes = len(sabotajes_recientes) * 0.25  # 0.25 por cada sabotaje
    peso_sabotajes = min(peso_sabotajes, 1.0)
    
    # 3. Factor de crisis financiera
    crisis = incidentes_infraestructura['crisis_financiera']
    peso_financiero = 0.0
    
    if crisis['calificacion_credito'] == 'PERDIDA':
        peso_financiero += 0.4
    if crisis['deuda_talara'] > 5e9:
        peso_financiero += 0.3
    if crisis['crecimiento_proyectado_2025'] == 0.0:
        peso_financiero += 0.3
    
    # ÍNDICE INTEGRADO
    # 30% Infraestructura vial
    # 40% Sabotajes ONP
    # 30% Crisis financiera
    
    risk_score = (0.30 * peso_derrumbes + 
                  0.40 * peso_sabotajes + 
                  0.30 * peso_financiero)
    
    # Clasificación
    if risk_score >= 0.75:
        risk_level = "CRÍTICO"
        color = "red"
    elif risk_score >= 0.55:
        risk_level = "ALTO"
        color = "orange"
    elif risk_score >= 0.35:
        risk_level = "MEDIO"
        color = "yellow"
    else:
        risk_level = "BAJO"
        color = "green"
    
    return {
        'score': risk_score,
        'level': risk_level,
        'color': color,
        'desglose': {
            'infraestructura_vial': peso_derrumbes,
            'sabotajes_onp': peso_sabotajes,
            'crisis_financiera': peso_financiero
        },
        'incidentes_recientes': {
            'derrumbes': len(derrumbes_recientes),
            'sabotajes': len(sabotajes_recientes)
        }
    }


def ajustar_recomendacion_con_riesgo_regional(score_base, confianza_base):
    """
    Ajusta el score de recomendación y confianza según riesgo regional.
    
    ENTRADA:
        score_base: float [0, 1] - Score original del sistema
        confianza_base: float [0, 100] - Confianza original del modelo
    
    RETORNA:
        score_ajustado: float [0, 1]
        confianza_ajustada: float [0, 100]
        advertencia: str (mensaje de alerta si aplica)
    """
    
    riesgo_peru = calcular_indice_riesgo_peru()
    
    # Ajuste de score: Si riesgo es alto, penalizar recomendaciones de COMPRA
    # y favorecer VENTA o MANTENER
    
    ajuste_score = 0.0
    advertencia = ""
    
    if riesgo_peru['level'] == "CRÍTICO":
        # Penalización fuerte (-15% al score)
        ajuste_score = -0.15
        advertencia = "⚠️ ALERTA CRÍTICA: Infraestructura petrolera en Perú en riesgo extremo. Considerar reducción de exposición."
        
    elif riesgo_peru['level'] == "ALTO":
        # Penalización moderada (-10% al score)
        ajuste_score = -0.10
        advertencia = "⚠️ ALERTA ALTA: Múltiples incidentes en infraestructura peruana. Monitorear evolución."
        
    elif riesgo_peru['level'] == "MEDIO":
        # Penalización leve (-5% al score)
        ajuste_score = -0.05
        advertencia = "ℹ️ Riesgo regional moderado en Perú. Sin impacto significativo en precio global."
    
    # Ajustar score
    score_ajustado = score_base + ajuste_score
    score_ajustado = max(0.0, min(1.0, score_ajustado))  # Clip a [0, 1]
    
    # Ajustar confianza: Reducir si hay alta incertidumbre regional
    reduccion_confianza = riesgo_peru['score'] * 15  # Hasta -15% de confianza
    confianza_ajustada = confianza_base - reduccion_confianza
    confianza_ajustada = max(0.0, min(100.0, confianza_ajustada))
    
    return {
        'score_ajustado': score_ajustado,
        'confianza_ajustada': confianza_ajustada,
        'ajuste_aplicado': ajuste_score,
        'advertencia': advertencia,
        'riesgo_regional': riesgo_peru
    }


def generar_reporte_riesgo_regional():
    """
    Genera reporte de consola sobre riesgo regional de Perú.
    """
    print("\n" + "="*80)
    print("ANÁLISIS DE RIESGO REGIONAL: PERÚ")
    print("="*80)
    
    riesgo = calcular_indice_riesgo_peru()
    
    print(f"\n🎯 NIVEL DE RIESGO: {riesgo['level']}")
    print(f"📊 Score de Riesgo: {riesgo['score']:.2f}")
    
    print(f"\n📋 DESGLOSE DE FACTORES:")
    print(f"  • Infraestructura Vial: {riesgo['desglose']['infraestructura_vial']:.2f}")
    print(f"  • Sabotajes ONP: {riesgo['desglose']['sabotajes_onp']:.2f}")
    print(f"  • Crisis Financiera: {riesgo['desglose']['crisis_financiera']:.2f}")
    
    print(f"\n📅 INCIDENTES RECIENTES:")
    print(f"  • Derrumbes (últimos 180d): {riesgo['incidentes_recientes']['derrumbes']}")
    print(f"  • Sabotajes ONP (últimos 90d): {riesgo['incidentes_recientes']['sabotajes']}")
    
    print("\n" + "="*80)
    
    return riesgo


# ══════════════════════════════════════════════════════════════════════════════
# EJEMPLO DE INTEGRACIÓN EN SISTEMA PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    # Mostrar reporte de riesgo regional
    riesgo = generar_reporte_riesgo_regional()
    
    # Ejemplo: Ajustar una recomendación
    print("\n" + "="*80)
    print("EJEMPLO: AJUSTE DE RECOMENDACIÓN")
    print("="*80)
    
    # Supongamos que el sistema original generó:
    score_original = 0.68  # COMPRAR (score >= 0.65)
    confianza_original = 85.0  # 85% de confianza
    
    print(f"\n📈 RECOMENDACIÓN ORIGINAL:")
    print(f"  Score: {score_original:.2f} → COMPRAR FUERTE")
    print(f"  Confianza: {confianza_original:.0f}%")
    
    # Aplicar ajuste por riesgo regional
    resultado = ajustar_recomendacion_con_riesgo_regional(score_original, confianza_original)
    
    print(f"\n📉 DESPUÉS DE AJUSTE POR RIESGO REGIONAL:")
    print(f"  Score Ajustado: {resultado['score_ajustado']:.2f}")
    print(f"  Confianza Ajustada: {resultado['confianza_ajustada']:.0f}%")
    print(f"  Ajuste Aplicado: {resultado['ajuste_aplicado']:+.2f}")
    
    if resultado['score_ajustado'] >= 0.65:
        decision = "COMPRAR FUERTE"
    elif resultado['score_ajustado'] >= 0.55:
        decision = "COMPRAR"
    elif resultado['score_ajustado'] > 0.45:
        decision = "MANTENER"
    else:
        decision = "VENDER"
    
    print(f"  Nueva Decisión: {decision}")
    
    if resultado['advertencia']:
        print(f"\n  {resultado['advertencia']}")
    
    print("\n" + "="*80)
    print("✅ Módulo de riesgo regional listo para integración")
    print("="*80)
