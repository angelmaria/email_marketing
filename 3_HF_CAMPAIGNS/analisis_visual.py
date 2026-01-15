"""
=============================================================================
ANÁLISIS VISUAL - HEALTHFINDER GALICIA
Visualizaciones para presentación y análisis pre-campaña
=============================================================================

Este script genera gráficos profesionales basados en la segmentación
Tier 1-4 de main.py (alineada con estrategia de 2 productos).

Ejecutar ANTES de lanzar campaña para:
- Validar segmentación visualmente
- Presentar a stakeholders
- Identificar oportunidades por provincia

"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
from pathlib import Path

# ============================================================================
# CONFIGURACIÓN
# ============================================================================

sns.set_style('whitegrid')
plt.rcParams['figure.figsize'] = (14, 8)
plt.rcParams['font.size'] = 11

OUTPUT_DIR = Path('output')
GRAFICOS_DIR = OUTPUT_DIR / 'graficos'
GRAFICOS_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = Path('data/farmacias_galicia.csv')

# ============================================================================
# FUNCIONES AUXILIARES (Reutilizadas de main.py)
# ============================================================================

def calculate_priority_score(row):
    """
    Calcula score de prioridad (MISMA LÓGICA que main.py).
    """
    rating = float(row.get('rating', 5.0)) or 5.0
    reviews = float(row.get('reviews', 0)) or 0
    has_web = str(row.get('site', '')).strip().lower() not in ('', 'null', 'none', 'nan')
    has_email = str(row.get('email', '')).strip().lower() not in ('', 'null', 'none', 'nan')
    
    # Base: cuanto menor el rating, más urgente
    rating_score = (5 - rating) * 20  # 0-100
    
    # Reseñas: menos reseñas = menos visibilidad
    reviews_score = min(50, reviews * 2)
    reviews_penalty = max(0, 50 - reviews_score)
    
    # Web es CRÍTICO
    web_factor = 30 if has_web else -50
    
    # Email es importante
    email_factor = 10 if has_email else 0
    
    total_score = rating_score + reviews_penalty + web_factor + email_factor
    total_score = max(0, min(100, total_score))
    
    # Asignar tier (MISMA LÓGICA que main.py)
    if has_web and rating < 4.0 and reviews < 30:
        tier = 'tier_1'
        tier_name = 'CRÍTICA'
    elif has_web and rating < 4.5:
        tier = 'tier_2'
        tier_name = 'ALTA'
    elif has_web:
        tier = 'tier_3'
        tier_name = 'MEDIA'
    else:
        tier = 'tier_4'
        tier_name = 'BAJA'
    
    return {
        'score': total_score,
        'tier': tier,
        'tier_name': tier_name,
        'has_web': has_web,
        'has_email': has_email,
    }

# ============================================================================
# CARGA Y PREPARACIÓN DE DATOS
# ============================================================================

print("="*80)
print("📊 ANÁLISIS VISUAL - HEALTHFINDER GALICIA")
print("="*80)
print(f"\n⏰ Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print(f"📂 Datos: {DATA_FILE}")
print(f"📁 Output: {GRAFICOS_DIR}")

df = pd.read_csv(DATA_FILE)
print(f"\n✅ Cargadas {len(df)} farmacias")

# Aplicar segmentación Tier 1-4
print("\n🔍 Aplicando segmentación Tier 1-4...")
df['priority_data'] = df.apply(calculate_priority_score, axis=1)
df['priority_score'] = df['priority_data'].apply(lambda x: x['score'])
df['priority_tier'] = df['priority_data'].apply(lambda x: x['tier'])
df['tier_name'] = df['priority_data'].apply(lambda x: x['tier_name'])
df['has_web'] = df['priority_data'].apply(lambda x: x['has_web'])
df['has_email'] = df['priority_data'].apply(lambda x: x['has_email'])

# Limpiar datos numéricos
for col in ['rating', 'reviews']:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

print("\n📊 Distribución por Tier:")
tier_counts = df['priority_tier'].value_counts().sort_index()
for tier in ['tier_1', 'tier_2', 'tier_3', 'tier_4']:
    count = tier_counts.get(tier, 0)
    tier_name = df[df['priority_tier'] == tier]['tier_name'].iloc[0] if count > 0 else 'N/A'
    print(f"   {tier_name:15} ({tier}): {count:4} farmacias")

# ============================================================================
# GRÁFICO 1: DISTRIBUCIÓN POR TIER (CRÍTICO PARA CAMPAÑA)
# ============================================================================

print("\n📈 Generando gráficos...")

fig, ax = plt.subplots(figsize=(12, 7))
tier_order = ['tier_1', 'tier_2', 'tier_3', 'tier_4']
tier_labels = ['CRÍTICA\n(Tier 1)', 'ALTA\n(Tier 2)', 'MEDIA\n(Tier 3)', 'BAJA\n(Tier 4)']
tier_colors = ['#e74c3c', '#e67e22', '#f39c12', '#95a5a6']

counts = [len(df[df['priority_tier'] == tier]) for tier in tier_order]

bars = ax.bar(tier_labels, counts, color=tier_colors, edgecolor='black', linewidth=1.5)

# Añadir valores en las barras
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

ax.set_title('Distribución de Farmacias por Prioridad (Tier 1-4)\nSegmentación para Campaña HF Galicia', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Nivel de Prioridad', fontsize=12)
ax.set_ylabel('Número de Farmacias', fontsize=12)
ax.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
plt.savefig(GRAFICOS_DIR / '01_distribucion_tiers.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 1: Distribución por Tier")
plt.close()

# ============================================================================
# GRÁFICO 2: DISTRIBUCIÓN POR PROVINCIA Y TIER (HEATMAP)
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 6))

# Crear tabla de contingencia
pivot = df.groupby(['provincia', 'priority_tier']).size().unstack(fill_value=0)
pivot = pivot.reindex(columns=tier_order, fill_value=0)

# Renombrar columnas
pivot.columns = ['CRÍTICA', 'ALTA', 'MEDIA', 'BAJA']

sns.heatmap(pivot, annot=True, fmt='d', cmap='YlOrRd', ax=ax, 
            cbar_kws={'label': 'Número de Farmacias'}, linewidths=0.5)

ax.set_title('Segmentación de Farmacias por Provincia y Tier\nOportunidades por Región', 
             fontsize=14, fontweight='bold', pad=15)
ax.set_xlabel('Nivel de Prioridad', fontsize=12)
ax.set_ylabel('Provincia', fontsize=12)
plt.tight_layout()
plt.savefig(GRAFICOS_DIR / '02_heatmap_provincia_tier.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 2: Heatmap Provincia x Tier")
plt.close()

# ============================================================================
# GRÁFICO 3: RATING VS RESEÑAS POR TIER (SCATTER)
# ============================================================================

fig, ax = plt.subplots(figsize=(14, 8))

for tier, color, label in zip(tier_order, tier_colors, tier_labels):
    data = df[df['priority_tier'] == tier]
    ax.scatter(data['reviews'], data['rating'], 
               alpha=0.6, s=60, color=color, label=label, edgecolor='black', linewidth=0.5)

ax.set_xlabel('Número de Reseñas', fontsize=12)
ax.set_ylabel('Rating (0-5)', fontsize=12)
ax.set_title('Rating vs Reseñas por Tier\nIdentificación de Oportunidades de Digital', 
             fontsize=14, fontweight='bold', pad=15)
ax.legend(title='Prioridad', fontsize=10, title_fontsize=11)
ax.grid(alpha=0.3, linestyle='--')

# Añadir líneas de referencia
ax.axhline(y=4.0, color='red', linestyle='--', linewidth=1, alpha=0.5, label='Rating crítico (4.0)')
ax.axvline(x=30, color='blue', linestyle='--', linewidth=1, alpha=0.5, label='Reseñas críticas (30)')

plt.tight_layout()
plt.savefig(GRAFICOS_DIR / '03_rating_vs_reviews_tier.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 3: Rating vs Reseñas por Tier")
plt.close()

# ============================================================================
# GRÁFICO 4: CTR ESPERADO POR TIER (PROYECCIÓN)
# ============================================================================

fig, ax = plt.subplots(figsize=(12, 7))

# CTR esperado según análisis (de ESTRATEGIA_2_vs_4_PRODUCTOS.md)
ctr_esperado = {
    'CRÍTICA\n(Tier 1)': 20,
    'ALTA\n(Tier 2)': 15,
    'MEDIA\n(Tier 3)': 10,
    'BAJA\n(Tier 4)': 5
}

bars = ax.bar(ctr_esperado.keys(), ctr_esperado.values(), 
              color=tier_colors, edgecolor='black', linewidth=1.5)

# Añadir valores
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height)}%',
            ha='center', va='bottom', fontsize=14, fontweight='bold')

ax.set_title('CTR Esperado por Tier\nProyección de Conversión Fase 1', 
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Nivel de Prioridad', fontsize=12)
ax.set_ylabel('CTR Esperado (%)', fontsize=12)
ax.set_ylim(0, 25)
ax.grid(axis='y', alpha=0.3, linestyle='--')

# Línea de referencia (promedio normal)
ax.axhline(y=5, color='green', linestyle='--', linewidth=2, 
           label='CTR normal (5%)', alpha=0.7)
ax.legend(fontsize=10)

plt.tight_layout()
plt.savefig(GRAFICOS_DIR / '04_ctr_esperado_tier.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 4: CTR Esperado por Tier")
plt.close()

# ============================================================================
# GRÁFICO 5: EMBUDO DE CONVERSIÓN (FASE 1)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 8))

# Datos del embudo (Tier 1+2, según RESUMEN_EJECUTIVO.md)
fase_1_farmacias = len(df[df['priority_tier'].isin(['tier_1', 'tier_2'])])
entrega_rate = 0.98
open_rate = 0.20
ctr = 0.05
demo_rate = 0.40
close_rate = 0.50

embudo = {
    'Emails enviados': fase_1_farmacias,
    'Entregados (98%)': int(fase_1_farmacias * entrega_rate),
    'Abiertos (20%)': int(fase_1_farmacias * entrega_rate * open_rate),
    'Clics (5%)': int(fase_1_farmacias * entrega_rate * open_rate * ctr),
    'Demos (40%)': int(fase_1_farmacias * entrega_rate * open_rate * ctr * demo_rate),
    'Ventas (50%)': int(fase_1_farmacias * entrega_rate * open_rate * ctr * demo_rate * close_rate)
}

stages = list(embudo.keys())
values = list(embudo.values())
colors = plt.cm.RdYlGn(np.linspace(0.3, 0.9, len(stages)))

y_pos = np.arange(len(stages))
bars = ax.barh(y_pos, values, color=colors, edgecolor='black', linewidth=1.5)

# Añadir valores
for i, (bar, value) in enumerate(zip(bars, values)):
    ax.text(value + 10, bar.get_y() + bar.get_height()/2, 
            f'{value}',
            va='center', fontsize=11, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(stages, fontsize=11)
ax.set_xlabel('Número de Farmacias / Conversiones', fontsize=12)
ax.set_title('Embudo de Conversión - Fase 1 (Tier 1+2)\nProyección de Resultados', 
             fontsize=14, fontweight='bold', pad=15)
ax.grid(axis='x', alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig(GRAFICOS_DIR / '05_embudo_conversion.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 5: Embudo de Conversión")
plt.close()

# ============================================================================
# GRÁFICO 6: DISPONIBILIDAD DE CONTACTO (EMAIL + TELÉFONO)
# ============================================================================

fig, ax = plt.subplots(figsize=(10, 7))

df['tiene_telefono'] = df['phone'].notna() & (df['phone'] != '')

contacto_stats = {
    'Email + Teléfono': len(df[(df['has_email']) & (df['tiene_telefono'])]),
    'Solo Email': len(df[(df['has_email']) & (~df['tiene_telefono'])]),
    'Solo Teléfono': len(df[(~df['has_email']) & (df['tiene_telefono'])]),
    'Sin Contacto': len(df[(~df['has_email']) & (~df['tiene_telefono'])])
}

labels = list(contacto_stats.keys())
sizes = list(contacto_stats.values())
colors_pie = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
explode = (0.05, 0, 0, 0.1)

wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors_pie,
                                    autopct='%1.1f%%', startangle=90,
                                    explode=explode, textprops={'fontsize': 11})

# Mejorar etiquetas
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')

ax.set_title('Disponibilidad de Contacto\nEmail vs Teléfono', 
             fontsize=14, fontweight='bold', pad=15)

plt.tight_layout()
plt.savefig(GRAFICOS_DIR / '06_disponibilidad_contacto.png', dpi=300, bbox_inches='tight')
print("   ✅ Gráfico 6: Disponibilidad de Contacto")
plt.close()

# ============================================================================
# EXPORTAR RESUMEN A EXCEL
# ============================================================================

print("\n📊 Exportando resumen a Excel...")

resumen = df.groupby('priority_tier').agg({
    'name': 'count',
    'rating': 'mean',
    'reviews': 'mean',
    'has_web': 'sum',
    'has_email': 'sum',
    'priority_score': 'mean'
}).round(2)

resumen.columns = ['Total Farmacias', 'Rating Promedio', 'Reseñas Promedio', 
                   'Con Web', 'Con Email', 'Score Promedio']

resumen.to_excel(OUTPUT_DIR / 'resumen_segmentacion.xlsx')
print(f"   ✅ Exportado: {OUTPUT_DIR / 'resumen_segmentacion.xlsx'}")

# ============================================================================
# RESUMEN FINAL
# ============================================================================

print("\n" + "="*80)
print("✅ ANÁLISIS VISUAL COMPLETADO")
print("="*80)
print(f"\n📁 Gráficos generados en: {GRAFICOS_DIR}/")
print(f"📊 Resumen Excel en: {OUTPUT_DIR}/resumen_segmentacion.xlsx")
print("\n📌 Gráficos generados:")
print("   1. Distribución por Tier (para stakeholders)")
print("   2. Heatmap Provincia x Tier (oportunidades regionales)")
print("   3. Rating vs Reseñas (identificación de oportunidades)")
print("   4. CTR Esperado por Tier (proyecciones)")
print("   5. Embudo de Conversión (resultados esperados)")
print("   6. Disponibilidad de Contacto (email vs teléfono)")
print("\n💡 Úsalos para presentaciones y análisis pre-campaña")
print("="*80 + "\n")
