"""
Script 0: Validación de Calidad de Datos
Valida que los datos descargados sean correctos antes de procesarlos
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("VALIDACIÓN DE CALIDAD DE DATOS")
print("=" * 70)

class ValidadorDatos:
    def __init__(self):
        self.errores = []
        self.advertencias = []
        self.datos_validos = True
    
    def validar_wti(self, ruta='base_datos_csv/petroleo/wti.csv'):
        """Valida datos de WTI"""
        print("\n[1/5] Validando WTI...")
        
        if not os.path.exists(ruta):
            self.errores.append(f"❌ Archivo no encontrado: {ruta}")
            self.datos_validos = False
            return
        
        df = pd.read_csv(ruta)
        
        # Check 1: Valores faltantes
        nulos = df.isnull().sum().sum()
        if nulos > 0:
            self.advertencias.append(f"⚠️  WTI: {nulos} valores faltantes")
        
        # Check 2: Duplicados
        duplicados = df.duplicated(subset=['fecha']).sum()
        if duplicados > 0:
            self.advertencias.append(f"⚠️  WTI: {duplicados} fechas duplicadas")
        
        # Check 3: Rango razonable (WTI entre $10-$150)
        if 'precio_cierre' in df.columns:
            fuera_rango = ((df['precio_cierre'] < 10) | (df['precio_cierre'] > 150)).sum()
            if fuera_rango > 0:
                self.advertencias.append(f"⚠️  WTI: {fuera_rango} precios fuera de rango razonable")
        
        # Check 4: Outliers con IQR
        if 'precio_cierre' in df.columns:
            Q1 = df['precio_cierre'].quantile(0.25)
            Q3 = df['precio_cierre'].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df['precio_cierre'] < Q1 - 1.5*IQR) | 
                       (df['precio_cierre'] > Q3 + 1.5*IQR)).sum()
            if outliers > 10:
                self.advertencias.append(f"⚠️  WTI: {outliers} outliers detectados (esperado en volatilidad)")
        
        # Check 5: Gaps temporales
        df['fecha'] = pd.to_datetime(df['fecha'])
        df = df.sort_values('fecha')
        gaps = (df['fecha'].diff() > timedelta(days=7)).sum()
        if gaps > 5:
            self.advertencias.append(f"⚠️  WTI: {gaps} gaps temporales >7 días")
        
        print(f"  ✓ WTI validado: {len(df)} registros")
        return df
    
    def validar_clientes(self, ruta='base_datos_csv/clientes.csv'):
        """Valida datos de clientes"""
        print("\n[2/5] Validando clientes...")
        
        if not os.path.exists(ruta):
            self.errores.append(f"❌ Archivo no encontrado: {ruta}")
            self.datos_validos = False
            return
        
        df = pd.read_csv(ruta)
        
        # Check 1: 1000 clientes esperados
        if len(df) != 1000:
            self.advertencias.append(f"⚠️  Clientes: Se esperaban 1000, encontrados {len(df)}")
        
        # Check 2: IDs únicos
        if df['cliente_id'].nunique() != len(df):
            self.errores.append("❌ Clientes: IDs duplicados")
            self.datos_validos = False
        
        # Check 3: Perfiles válidos
        perfiles_validos = ['Conservador', 'Moderado', 'Agresivo']
        if 'tipo_inversor' in df.columns:
            invalidos = (~df['tipo_inversor'].isin(perfiles_validos)).sum()
            if invalidos > 0:
                self.errores.append(f"❌ Clientes: {invalidos} perfiles inválidos")
                self.datos_validos = False
        
        # Check 4: Capital razonable
        if 'capital_inicial' in df.columns:
            if (df['capital_inicial'] < 0).any():
                self.errores.append("❌ Clientes: Capital negativo detectado")
                self.datos_validos = False
        
        print(f"  ✓ Clientes validados: {len(df)} registros")
        return df
    
    def validar_predicciones(self, ruta='base_datos_csv/predicciones_prophet.csv'):
        """Valida predicciones de Prophet"""
        print("\n[3/5] Validando predicciones Prophet...")
        
        if not os.path.exists(ruta):
            self.advertencias.append(f"⚠️  Predicciones no generadas aún: {ruta}")
            return None
        
        df = pd.read_csv(ruta)
        
        # Check 1: Fechas futuras
        df['fecha'] = pd.to_datetime(df['fecha'])
        futuras = (df['fecha'] > datetime.now()).sum()
        if futuras == 0:
            self.advertencias.append("⚠️  Predicciones: No hay fechas futuras")
        
        # Check 2: Intervalos de confianza
        if all(col in df.columns for col in ['precio_predicho', 'limite_inferior', 'limite_superior']):
            invalidos = (df['limite_inferior'] > df['precio_predicho']).sum()
            invalidos += (df['precio_predicho'] > df['limite_superior']).sum()
            if invalidos > 0:
                self.errores.append(f"❌ Predicciones: {invalidos} intervalos inválidos")
                self.datos_validos = False
        
        print(f"  ✓ Predicciones validadas: {len(df)} registros")
        return df
    
    def validar_sentimientos(self, ruta='base_datos_csv/sentimientos.csv'):
        """Valida análisis de sentimiento"""
        print("\n[4/5] Validando sentimientos...")
        
        if not os.path.exists(ruta):
            self.advertencias.append(f"⚠️  Sentimientos no generados aún: {ruta}")
            return None
        
        df = pd.read_csv(ruta)
        
        # Check 1: Scores en rango [-1, +1]
        if 'score_compound' in df.columns:
            fuera_rango = ((df['score_compound'] < -1) | (df['score_compound'] > 1)).sum()
            if fuera_rango > 0:
                self.errores.append(f"❌ Sentimientos: {fuera_rango} scores fuera de rango")
                self.datos_validos = False
        
        # Check 2: Clasificaciones válidas
        if 'clasificacion' in df.columns:
            validos = ['POSITIVO', 'NEGATIVO', 'NEUTRAL']
            invalidos = (~df['clasificacion'].isin(validos)).sum()
            if invalidos > 0:
                self.errores.append(f"❌ Sentimientos: {invalidos} clasificaciones inválidas")
                self.datos_validos = False
        
        print(f"  ✓ Sentimientos validados: {len(df)} registros")
        return df
    
    def validar_recomendaciones(self, ruta='base_datos_csv/recomendaciones.csv'):
        """Valida recomendaciones"""
        print("\n[5/5] Validando recomendaciones...")
        
        if not os.path.exists(ruta):
            self.advertencias.append(f"⚠️  Recomendaciones no generadas aún: {ruta}")
            return None
        
        df = pd.read_csv(ruta)
        
        # Check 1: Scores en rango [0, 5]
        if 'score' in df.columns:
            fuera_rango = ((df['score'] < 0) | (df['score'] > 5)).sum()
            if fuera_rango > 0:
                self.errores.append(f"❌ Recomendaciones: {fuera_rango} scores fuera de rango")
                self.datos_validos = False
        
        print(f"  ✓ Recomendaciones validadas: {len(df)} registros")
        return df
    
    def generar_reporte(self):
        """Genera reporte final"""
        print("\n" + "=" * 70)
        print("REPORTE DE VALIDACIÓN")
        print("=" * 70)
        
        if self.datos_validos:
            print("\n✅ VALIDACIÓN EXITOSA")
            print("   Todos los datos están correctos y listos para usar")
        else:
            print("\n❌ VALIDACIÓN FALLIDA")
            print("   Se encontraron errores críticos")
        
        if self.errores:
            print(f"\n🔴 ERRORES ({len(self.errores)}):")
            for error in self.errores:
                print(f"   {error}")
        
        if self.advertencias:
            print(f"\n🟡 ADVERTENCIAS ({len(self.advertencias)}):")
            for advertencia in self.advertencias:
                print(f"   {advertencia}")
        
        if not self.errores and not self.advertencias:
            print("\n🎉 Perfecto! No se encontraron problemas")
        
        print("\n" + "=" * 70)
        
        # Guardar reporte en archivo
        with open('base_datos_csv/quality_report.txt', 'w', encoding='utf-8') as f:
            f.write("REPORTE DE CALIDAD DE DATOS\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 70 + "\n\n")
            
            if self.datos_validos:
                f.write("Estado: ✅ VALIDACIÓN EXITOSA\n\n")
            else:
                f.write("Estado: ❌ VALIDACIÓN FALLIDA\n\n")
            
            if self.errores:
                f.write(f"ERRORES ({len(self.errores)}):\n")
                for error in self.errores:
                    f.write(f"  {error}\n")
                f.write("\n")
            
            if self.advertencias:
                f.write(f"ADVERTENCIAS ({len(self.advertencias)}):\n")
                for advertencia in self.advertencias:
                    f.write(f"  {advertencia}\n")
        
        print("📄 Reporte guardado en: base_datos_csv/quality_report.txt")
        
        return self.datos_validos

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    validador = ValidadorDatos()
    
    # Validar cada componente
    validador.validar_wti()
    validador.validar_clientes()
    validador.validar_predicciones()
    validador.validar_sentimientos()
    validador.validar_recomendaciones()
    
    # Generar reporte
    exito = validador.generar_reporte()
    
    # Exit code
    exit(0 if exito else 1)
