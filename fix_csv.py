import csv
from datetime import datetime

# Leer el CSV original
with open('contactos.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# Fecha de hoy
fecha_hoy = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Encontrar el índice de info@farmav30.com
target_index = None
for i, row in enumerate(rows):
    if 'info@farmav30.com' in row.get('Email', ''):
        target_index = i
        break

print(f"Encontrado info@farmav30.com en línea {target_index + 2} (índice {target_index})")
print(f"Marcando como enviados los primeros {target_index + 1} contactos")

# Añadir las columnas a todas las filas
for i, row in enumerate(rows):
    if i <= target_index:
        row['enviado_c1'] = 'si'
        row['fecha_enviado_c1'] = fecha_hoy
    else:
        row['enviado_c1'] = ''
        row['fecha_enviado_c1'] = ''

# Escribir el CSV actualizado
fieldnames = list(rows[0].keys())
with open('contactos.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Archivo actualizado. {target_index + 1} contactos marcados como enviados.")
print(f"📧 Pendientes de envío: {len(rows) - target_index - 1}")
