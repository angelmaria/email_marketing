# ============================================================================
# SCRIPT AVANZADO CON VISUALIZACIONES - OPCIONAL
# ============================================================================
# Este script añade gráficos y análisis más profundos
# Requiere: pip install pandas openpyxl matplotlib seaborn
# ============================================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

# Configuración de estilo
sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

os.makedirs('output/graficos', exist_ok=True)

print("🚀 INICIANDO ANÁLISIS AVANZADO CON VISUALIZACIONES")
print("="*70)

# Cargar datos (reutilizar el código de limpieza del script anterior)
df = pd.read_csv('data/farmacias_galicia.csv')

# Función de limpieza
def limpiar_numerico(serie):
    if serie.dtype == 'object':
        return pd.to_numeric(
            serie.astype(str).str.replace('.', '', regex=False).str.replace(',', '.', regex=False),
            errors='coerce'
        )
    return serie

cols_numericas = ['rating', 'reviews', 'porc_poblacion_65_mas', 'renta_neta_total_personas_portal']
for col in cols_numericas:
    if col in df.columns:
        df[col] = limpiar_numerico(df[col])

df = df.drop_duplicates(subset=['google_id'], keep='first')

# ============================================================================
# VISUALIZACIONES
# ============================================================================

print("\n📊 Generando visualizaciones...")

# 1. Distribución de farmacias por provincia
fig, ax = plt.subplots()
df['provincia'].value_counts().plot(kind='bar', ax=ax, color='steelblue')
ax.set_title('Distribución de Farmacias por Provincia', fontsize=14, fontweight='bold')
ax.set_xlabel('Provincia')
ax.set_ylabel('Número de Farmacias')
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('output/graficos/01_distribucion_provincias.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 1: Distribución por provincia")
plt.close()

# 2. Rating vs Reseñas (scatter plot)
fig, ax = plt.subplots()
for provincia in df['provincia'].unique():
    data = df[df['provincia'] == provincia]
    ax.scatter(data['reviews'], data['rating'], alpha=0.6, label=provincia, s=50)
ax.set_xlabel('Número de Reseñas')
ax.set_ylabel('Rating')
ax.set_title('Rating vs Reseñas por Provincia', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('output/graficos/02_rating_vs_resenas.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 2: Rating vs Reseñas")
plt.close()

# 3. Distribución de ratings
fig, ax = plt.subplots()
df['rating'].hist(bins=20, ax=ax, color='coral', edgecolor='black')
ax.set_xlabel('Rating')
ax.set_ylabel('Frecuencia')
ax.set_title('Distribución de Ratings', fontsize=14, fontweight='bold')
ax.axvline(df['rating'].mean(), color='red', linestyle='--', linewidth=2, label=f'Media: {df["rating"].mean():.2f}')
ax.legend()
ax.grid(axis='y', alpha=0.3)
plt.tight_layout()
plt.savefig('output/graficos/03_distribucion_ratings.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 3: Distribución de ratings")
plt.close()

# 4. Heatmap de segmentación
df['tiene_email'] = df['email'].notna() & (df['email'] != '')
df['prioridad_campana'] = df.apply(
    lambda row: 'ALTA' if row['rating'] >= 4.8 and row['reviews'] >= 20
                else 'MEDIA' if row['rating'] >= 4.5 and row['reviews'] >= 10
                else 'BAJA' if row['rating'] >= 4.0
                else 'NO CONTACTAR',
    axis=1
)

segmentacion = df.groupby(['provincia', 'prioridad_campana']).size().unstack(fill_value=0)

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(segmentacion, annot=True, fmt='d', cmap='YlOrRd', ax=ax, cbar_kws={'label': 'Número de Farmacias'})
ax.set_title('Segmentación de Farmacias por Provincia y Prioridad', fontsize=14, fontweight='bold')
ax.set_xlabel('Prioridad de Campaña')
ax.set_ylabel('Provincia')
plt.tight_layout()
plt.savefig('output/graficos/04_heatmap_segmentacion.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 4: Heatmap de segmentación")
plt.close()

# 5. Boxplot de renta por provincia
fig, ax = plt.subplots(figsize=(10, 6))
df.boxplot(column='renta_neta_total_personas_portal', by='provincia', ax=ax)
ax.set_title('Distribución de Renta por Provincia', fontsize=14, fontweight='bold')
ax.set_xlabel('Provincia')
ax.set_ylabel('Renta Neta (Portal)')
plt.suptitle('')  # Quitar título automático
plt.tight_layout()
plt.savefig('output/graficos/05_renta_por_provincia.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 5: Renta por provincia")
plt.close()

print("\n" + "="*70)
print("✅ VISUALIZACIONES GENERADAS EN output/graficos/")
print("="*70)
print("\n💡 Usa estos gráficos para presentaciones y reportes")
print("="*70 + "\n")