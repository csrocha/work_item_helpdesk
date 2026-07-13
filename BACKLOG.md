# BACKLOG

Ideas y mejoras propuestas para `work_item_helpdesk` que todavía no se
implementaron. Primer archivo de este tipo para este módulo (mismo
formato que `insight_project/BACKLOG.md`).

---

## Del backlog de ecosistema (2026-07-13)

Propuesta de "nivel profesional superior" para todo el ecosistema. Visión
completa en la memoria `project_ecosystem_roadmap`.

### 1. Revisar el escape HTML en `_work_item_compose_message`

Confirmado por auditoría de código (2026-07-13):
`models/helpdesk_ticket.py:41` `_work_item_compose_message` arma el body
como `str` plano (`'<br/>'.join(...)`) y lo pasa directo a
`message_post(body=...)` (línea 38) — sin envolver en
`markupsafe.Markup`. Por contraste,
`insight_project_purchase/models/project_project.py`
`_post_purchase_confirmed_message` sí hace
`Markup('<br/>').join(lines)` correctamente. Mismo patrón de bug ya
encontrado y corregido una vez en este ecosistema (ver memoria
`project_message_post_html_escaping`): sin `Markup`, Odoo escapa el HTML
plano y los `<br/>` se ven como texto literal en el chatter en vez de
salto de línea. Falta confirmar en un chatter real (no alcanza con leer
el código) y corregir si el síntoma se reproduce.

_Fuente: backlog de ecosistema propuesto por el usuario (2026-07-13,
"Épica 6" ítem 3)._
