from odoo import fields, models, api

class ArbaAlicuot (models.Model):
    _name = "arba.alicuot"
    _description = "Alicuotas de percepcion y retencion"

    company_id = fields.Many2one("res.company")
    tax_id = fields.Many2one("account.tax", domain="[('type_tax_use', '=', 'none')]")
    alicuot_perception = fields.Float()
    alicuot_retencion = fields.Float()
    witholding_amount_type = fields.Selection(
        selection=[("total_amount", "Cantidad Total"), ("untaxed_amount", "Monto libre de impuestos")]
    )
    partner_id = fields.Many2one("res.partner", copy=False, required=True, ondelete="cascade")
    date_from = fields.Date(copy=False)
    date_to = fields.Date(copy=False)
    from_padron = fields.Boolean(copy=False)
    regimen = fields.Selection(
        selection=[("percepcion", "Percepcion"), ("retencion", "Retencion")]
    )

