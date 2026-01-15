# 📧 Gmail Campaigns V1 (PROYECTO FALLIDO - ARCHIVADO)

## ⚠️ ESTADO: ARCHIVADO

Este proyecto fue descontinuado tras múltiples intentos fallidos.  
**NO USAR EN PRODUCCIÓN** - Solo para referencia histórica.

---

## 🚫 ¿Por qué falló?

### 1. Bloqueo de IP por Gmail

**Problema**: Al enviar >500 emails/día desde gmail.com personal, Google bloqueó la cuenta.

**Señales de bloqueo**:
- Error: "SMTPAuthenticationError: 535-5.7.8 Username and Password not accepted"
- Emails marcados automáticamente como spam
- Rate limit reducido de 500 a 100/día sin previo aviso

### 2. Mala calidad de datos

**Problema**: ~30% de emails inválidos o bounced.

**Impacto**:
- Reputación del dominio dañada
- Tasa de entrega: 68% (objetivo: >95%)
- Reintentos automáticos agravaron el bloqueo

### 3. Estrategia de 4 productos

**Problema**: Ofrecer 4 servicios simultáneos diluyó el mensaje.

**Resultados medidos**:
- Open rate: 12% (benchmark: 18%)
- CTR: 1.8% (benchmark: 5%)
- Conversión: 0 demos agendadas de 200 emails enviados

---

## 📊 Métricas Finales

| Métrica | Resultado | Esperado | Gap |
|---------|-----------|----------|-----|
| Emails enviados | 200 | 500 | -60% (bloqueado) |
| Tasa de entrega | 68% | 95% | **-27%** |
| Open rate | 12% | 18% | -6% |
| CTR | 1.8% | 5% | **-3.2%** |
| Demos agendadas | 0 | 5 | **-5** |
| Ventas cerradas | 0 | 2 | -2 |

**Costo total**: €150 (tiempo + herramientas)  
**Ingresos**: €0  
**ROI**: -100%

---

## 🎓 Lecciones Aprendidas

### ✅ QUÉ FUNCIONÓ

1. **Segmentación por Google Business rating**: Tier system tiene sentido (reusado en HF)
2. **Personalización**: Emails con nombre de farmacia tuvieron +20% open rate vs genéricos
3. **Templates HTML responsive**: Buenos para reutilizar

### ❌ QUÉ NO FUNCIONÓ

1. **Gmail personal**: Usar email corporativo (ej: @novaquality.es) es CRÍTICO
2. **4 productos en 1 email**: Sobrecarga cognitiva → Reducir a 2 máximo
3. **Sin warm-up de IP**: Enviar 500 emails el día 1 → Spam flag inmediato
4. **Bounce handling**: No validamos emails antes de enviar → Reputación dañada

---

## 🔄 Migración a Healthfinder (HF)

Este proyecto evolucionó a **3_HF_CAMPAIGNS** con correcciones:

| Problema Gmail V1 | Solución HF V2 |
|------------------|---------------|
| Gmail personal bloqueado | Email corporativo @novaquality.es |
| 4 productos (confuso) | 2 productos (Digital + Pedidos) |
| Sin rate limiting | 50 emails/día con delays |
| 30% emails inválidos | Pre-validación con regex + verificación SMTP |
| Open rate 12% | Target 20% (email corporativo + mejor copy) |
| CTR 1.8% | Target 5% (2 CTAs claros) |

---

## 📁 Estructura Archivada

```
1_GMAIL_CAMPAIGNS_V1/
├── README.md                    # Este archivo
├── main.py                      # Script original (NO USAR)
├── email_sender.py              # Reutilizable si necesario
├── requirements.txt
├── data/
│   └── contactos_originales.csv # Datos históricos
├── TEMPLATES/
│   └── email_camp_1.html        # Template 4 productos
├── IMAGENES/
│   └── logo_healthfinder.png
└── logs/
    └── campaign_tracking_*.csv  # Histórico de envíos
```

---

## 🚀 ¿Quieres replicar este proyecto?

**NO** - Usa [3_HF_CAMPAIGNS](../3_HF_CAMPAIGNS/README.md) en su lugar.

Si insistes en usar Gmail personal:
1. **Warm-up de IP**: Enviar 10-20 emails/día durante 2 semanas antes de escalar
2. **Validar emails**: Usar API de ZeroBounce o similar (€0.01/email)
3. **Max 100 emails/día**: No arriesgues bloqueo permanente
4. **Enable "Less secure apps"**: En Google Account Settings (NO recomendado)

---

## 📚 Recursos Relacionados

- [Lecciones Aprendidas Completas](../DOCS/LECCIONES_APRENDIDAS.md)
- [Healthfinder Campaign V2](../3_HF_CAMPAIGNS/README.md)
- [Email Marketing Best Practices](../DOCS/EMAIL_MARKETING_GUIDE.md)

---

**Archivado**: 2025-01-XX  
**Última campaña**: 2024-12-XX  
**Razón de cierre**: Bloqueo de IP + ROI negativo
