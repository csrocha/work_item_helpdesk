# Work Item Systray — Helpdesk

Proveedor de [`work_item_systray`](https://github.com/csrocha/work_item_systray):
convierte `helpdesk.ticket` en un work item trabajable desde el mismo
systray que las tareas, sin que `work_item_systray` (ni ningún otro
proveedor, como `work_item_task`/`insight_project`) tenga que depender de
`helpdesk`.

- **Candidatos**: mis tickets abiertos (`user_id` = usuario actual,
  `stage_id.fold = False`).
- **Cierre de período**: postea un mensaje en el chatter del ticket
  combinando la nota de inicio ("qué se iba a hacer") con la de cierre
  ("qué se logró") y la duración trabajada. Si el módulo
  `helpdesk_timesheet` está instalado y el ticket tiene un `task_id`
  (proyecto sombra que crea ese módulo), además registra una línea de
  `account.analytic.line` para que el tiempo cuente en los partes de horas.
- **Cronómetro**: siempre ascendente — este addon no aporta
  `allocated_hours`/`remaining_hours`, así que nunca activa la cuenta
  regresiva de `work_item_task`.

Sin JS propio: la lista de tickets se renderiza con el template genérico
del systray base.

## License

OPL-1 — Cristian S. Rocha <csrocha@gmail.com>
