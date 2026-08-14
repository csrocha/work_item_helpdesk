# -*- coding: utf-8 -*-
"""_work_item_compose_message debía usar str plano ('<br/>'.join(...)),
que odoo.mail.thread.message_post escapa por completo — los <br/> se veían
como texto literal en el chatter (ver memoria
message-post-html-escaping). Fix: Markup('<br/>').join(...), que además
escapa cada parte (intent_note/outcome_note son texto libre del usuario)."""
from markupsafe import Markup

from odoo.fields import Datetime
from odoo.tests.common import TransactionCase


class TestHelpdeskTicketComposeMessage(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ticket = cls.env['helpdesk.ticket'].create({'name': 'Test ticket'})

    def test_compose_message_is_markup_with_real_line_breaks(self):
        body = self.ticket._work_item_compose_message(
            Datetime.now(), 'arrancar', 'terminado',
        )
        self.assertIsInstance(body, Markup)
        self.assertIn('<br/>', body)

    def test_compose_message_escapes_user_supplied_notes(self):
        body = self.ticket._work_item_compose_message(
            Datetime.now(), '<script>alert(1)</script>', None,
        )
        self.assertNotIn('<script>', body)
        self.assertIn('&lt;script&gt;', body)


class TestHelpdeskTicketWorkItemCandidates(TransactionCase):
    """BACKLOG.md (work_item_systray) ítem 2.4: _get_switchable_work_items
    ordena por prioridad usando la clave 'priority' de cada candidato --
    faltaba en helpdesk.ticket."""

    def test_candidate_carries_priority(self):
        ticket = self.env['helpdesk.ticket'].create({
            'name': 'Test ticket', 'user_id': self.env.uid, 'priority': '2',
        })
        by_id = {c['res_id']: c for c in self.env['helpdesk.ticket']._work_item_candidates()}
        self.assertEqual(by_id[ticket.id]['priority'], '2')
