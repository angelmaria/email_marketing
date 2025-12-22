import csv
import argparse
from datetime import datetime
from pathlib import Path

CSV_PATH = Path(__file__).resolve().parent / 'contactos.csv'
CAMPAIGN_COL = 'enviado_c1'
DATE_COL = 'fecha_enviado_c1'


def main(target_email: str):
    target_email_l = target_email.strip().lower()

    with open(CSV_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = reader.fieldnames or []

    if CAMPAIGN_COL not in fieldnames:
        fieldnames.append(CAMPAIGN_COL)
    if DATE_COL not in fieldnames:
        fieldnames.append(DATE_COL)

    found_index = None
    for i, row in enumerate(rows):
        emails = (row.get('Email') or '').lower()
        if target_email_l in emails:
            found_index = i
            break

    if found_index is None:
        print(f"❌ No se encontró '{target_email}' en la columna Email.")
        return 1

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    for i, row in enumerate(rows):
        if i <= found_index:
            row[CAMPAIGN_COL] = 'si'
            row[DATE_COL] = now
        else:
            # Mantener lo existente si ya estaba marcado; si no, en blanco
            if row.get(CAMPAIGN_COL, '').strip().lower() != 'si':
                row[CAMPAIGN_COL] = ''
                row[DATE_COL] = ''

    with open(CSV_PATH, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✅ Marcadas {found_index + 1} filas como enviadas hasta '{target_email}'.")
    print(f"📄 Archivo actualizado: {CSV_PATH}")
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Marca contactos.csv como enviado hasta un email dado (inclusive).')
    parser.add_argument('--target', required=True, help='Email hasta el que marcar como enviado (inclusive).')
    args = parser.parse_args()
    raise SystemExit(main(args.target))
