# -*- coding: utf-8 -*-
import re
from html import unescape

from odoo import _, api, fields, models

_TAG_RE = re.compile(r'<[^>]+>')
_SPACE_RE = re.compile(r'\s+')


def _html_to_text(html_value, max_len=280):
    if not html_value:
        return ''
    text = unescape(_TAG_RE.sub(' ', html_value))
    text = _SPACE_RE.sub(' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rstrip() + '…'
    return text


class HelpdeskTicket(models.Model):
    _inherit = ['helpdesk.ticket', 'work.item.mixin']

    def _work_item_label(self):
        self.ensure_one()
        return {
            'name': self.name,
            'icon': '🎫',
            'css_class': 'text-danger fw-bold' if int(self.priority or 0) >= 2 else '',
            'description': _html_to_text(self.description),
        }

    def _work_item_close(self, start_datetime, intent_note, outcome_note, outcome_blocked):
        """Deja constancia en el chatter del ticket y, si helpdesk_timesheet
        está instalado, además registra la línea de parte de horas."""
        self.ensure_one()
        self.message_post(body=self._work_item_compose_message(start_datetime, intent_note, outcome_note))
        self._work_item_log_timesheet(start_datetime, intent_note, outcome_note)

    def _work_item_compose_message(self, start_datetime, intent_note, outcome_note):
        self.ensure_one()
        duration = (fields.Datetime.now() - start_datetime).total_seconds() / 3600.0
        parts = [_('Se trabajó %.2f h en este ticket.') % duration]
        if intent_note:
            parts.append(_('Se quiso hacer: %s.') % intent_note)
        if outcome_note:
            parts.append(_('Se logró: %s.') % outcome_note)
        return '<br/>'.join(parts)

    def _work_item_log_timesheet(self, start_datetime, intent_note, outcome_note):
        """helpdesk_timesheet (opcional, no declarado en depends) agrega
        account.analytic.line.helpdesk_ticket_id + helpdesk.ticket.project_id;
        si no está instalado, no hay dónde registrar la línea y se omite."""
        self.ensure_one()
        AnalyticLine = self.env['account.analytic.line']
        if 'helpdesk_ticket_id' not in AnalyticLine._fields or not self.project_id:
            return
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.uid)], limit=1
        )
        if not employee:
            return
        duration = (fields.Datetime.now() - start_datetime).total_seconds() / 3600.0
        if duration <= 0:
            return
        name = self.name or _('Trabajo registrado')
        if intent_note or outcome_note:
            parts = []
            if intent_note:
                parts.append(_('Se quiso hacer: %s.') % intent_note)
            if outcome_note:
                parts.append(_('Se logró: %s.') % outcome_note)
            name = ' '.join(parts)
        AnalyticLine.sudo().create({
            'name': name,
            'project_id': self.project_id.id,
            'helpdesk_ticket_id': self.id,
            'employee_id': employee.id,
            'unit_amount': duration,
            'date': start_datetime.date(),
        })

    @api.model
    def _work_item_candidates(self):
        """Mis tickets abiertos (no en una etapa plegada/cerrada)."""
        tickets = self.search([
            ('user_id', '=', self.env.uid),
            ('stage_id.fold', '=', False),
        ])
        return [{
            'res_id': t.id,
            'name': t.name,
            'icon': '🎫',
            'css_class': 'text-danger' if int(t.priority or 0) >= 2 else '',
        } for t in tickets]

    def action_switch_to_session(self):
        """Activa este ticket en la sesión del systray del usuario actual."""
        self.ensure_one()
        self.env['work.item.session'].action_switch_work_item('helpdesk.ticket', self.id)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Ticket activado'),
                'message': _('Ahora estás trabajando en "%s".') % self.name,
                'type': 'success',
                'sticky': False,
            },
        }
