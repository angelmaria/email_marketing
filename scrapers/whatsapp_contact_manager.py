#!/usr/bin/env python3
"""
WhatsApp Contact Manager
Gestiona y rastrea contactos para campañas de WhatsApp.
Permite marcar farmacias como "contactadas", filtrar por provincia/CP, etc.
"""

import csv
from pathlib import Path
from datetime import datetime
import sys

FARMACIAS_FILE = 'farmacias_españa_whatsapp.csv'
LOGS_DIR = Path('logs_whatsapp')

def cargar_farmacias():
    """Carga el CSV de farmacias."""
    if not Path(FARMACIAS_FILE).exists():
        print(f"❌ No existe {FARMACIAS_FILE}")
        return []
    
    with open(FARMACIAS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def guardar_farmacias(farmacias):
    """Guarda cambios en el CSV."""
    if not farmacias:
        return
    
    with open(FARMACIAS_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=farmacias[0].keys())
        writer.writeheader()
        writer.writerows(farmacias)
    print(f"✅ {FARMACIAS_FILE} actualizado")

def obtener_sin_contactar(provincia=None):
    """Retorna farmacias sin contactar, opcionalmente filtradas por provincia."""
    farmacias = cargar_farmacias()
    
    sin_contactar = [f for f in farmacias if f.get('Contactado', 'No').lower() == 'no' and f.get('Telefonos', '').strip()]
    
    if provincia:
        sin_contactar = [f for f in sin_contactar if f.get('Provincia', '').lower() == provincia.lower()]
    
    return sin_contactar

def marcar_contactadas(telefonos):
    """Marca farmacias como contactadas por su teléfono."""
    farmacias = cargar_farmacias()
    contador = 0
    
    for farmacia in farmacias:
        tels = [t.strip() for t in farmacia.get('Telefonos', '').split(';') if t.strip()]
        if any(tel in telefonos for tel in tels):
            farmacia['Contactado'] = 'Sí'
            contador += 1
    
    guardar_farmacias(farmacias)
    print(f"✅ {contador} farmacias marcadas como contactadas")

def estadisticas():
    """Muestra estadísticas de progreso."""
    farmacias = cargar_farmacias()
    
    total = len(farmacias)
    con_telefono = len([f for f in farmacias if f.get('Telefonos', '').strip()])
    contactadas = len([f for f in farmacias if f.get('Contactado', 'No').lower() == 'sí'])
    sin_contactar = len([f for f in farmacias if f.get('Contactado', 'No').lower() == 'no' and f.get('Telefonos', '').strip()])
    
    print(f"\n📊 ESTADÍSTICAS GENERALES")
    print(f"   Total farmacias: {total}")
    print(f"   Con teléfono: {con_telefono} ({con_telefono/total*100:.1f}%)")
    print(f"   Contactadas: {contactadas} ({contactadas/con_telefono*100:.1f}% si hay teléfono)")
    print(f"   Sin contactar: {sin_contactar}")
    
    # Por provincia
    provincias = {}
    for f in farmacias:
        prov = f.get('Provincia', 'Desconocida')
        if prov not in provincias:
            provincias[prov] = {'total': 0, 'con_tel': 0, 'contactadas': 0}
        provincias[prov]['total'] += 1
        if f.get('Telefonos', '').strip():
            provincias[prov]['con_tel'] += 1
        if f.get('Contactado', 'No').lower() == 'sí':
            provincias[prov]['contactadas'] += 1
    
    print(f"\n📍 POR PROVINCIA")
    for prov, datos in sorted(provincias.items()):
        print(f"   {prov}: {datos['total']} ({datos['con_tel']} con tel, {datos['contactadas']} contactadas)")

def exportar_para_contactar(provincia=None, limite=50):
    """Exporta lista de contactos para enviar mensajes."""
    sin_contactar = obtener_sin_contactar(provincia)
    
    muestra = sin_contactar[:limite]
    
    output_file = f"contactos_pendientes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=muestra[0].keys() if muestra else [])
        if muestra:
            writer.writeheader()
            writer.writerows(muestra)
    
    print(f"✅ Exportados {len(muestra)} contactos en {output_file}")
    
    if provincia:
        print(f"   Provincia: {provincia}")
    print(f"   Primero contacta estos y marca como 'Sí' en la columna 'Contactado'")
    print(f"   Luego ejecuta: python whatsapp_contact_manager.py marcar <telefonos_separados_por_comas>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso:")
        print("  python whatsapp_contact_manager.py stats              # Ver estadísticas")
        print("  python whatsapp_contact_manager.py exportar [PROV] [N]  # Exportar N contactos (ej: Madrid 50)")
        print("  python whatsapp_contact_manager.py marcar <TELS>     # Marcar como contactadas (ej: '+34666666666,+34777777777')")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'stats':
        estadisticas()
    elif cmd == 'exportar':
        prov = sys.argv[2] if len(sys.argv) > 2 else None
        limite = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        exportar_para_contactar(prov, limite)
    elif cmd == 'marcar':
        if len(sys.argv) < 3:
            print("Proporciona teléfonos separados por comas")
            sys.exit(1)
        telefonos = [t.strip() for t in sys.argv[2].split(',')]
        marcar_contactadas(telefonos)
    else:
        print(f"Comando desconocido: {cmd}")
