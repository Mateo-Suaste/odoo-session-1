from odoo import fields, models

class AccountPadron (models.Model):
    _name = "account.padron"
    _description = "Padron of the alicuo per and ret"

    partner_updated = fields.Boolean()
    from_padron_import = fields.Boolean()
    tax = fields.Char()
    marc_subject = fields.Char()
    display_name = fields.Char()
    cuit = fields.Char()
    const_type = fields.Char()
    date_p = fields.Date()
    date_from = fields.Date()
    date_to = fields.Date()
    padron_import_id = fields.Integer()
    company_id = fields.Many2one("res.company", string="Empresa")
    regimen = fields.Selection(
        string="Regimen",
        selection=[("retencion", "Retencion"), ("percepcion", "Percepcion")]
    )
    marc_change_alic = fields.Selection(
        string="Marca cambio alícuota",
        selection=[("si", "Si"), ("no", "No")]
    )
    percent = fields.Float()
