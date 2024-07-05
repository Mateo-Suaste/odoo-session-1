from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    tax_retencion_id = fields.Many2one(
        "account.tax", 
        domain="[('type_tax_use', '=', 'none')]", 
        string="Impuesto de Retención"
    )
    tax_perception_id = fields.Many2one(
        "account.tax", 
        domain="[('type_tax_use', '=', 'none')]", 
        string="Impuesto de Percepción"
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        tax_retencion_id = ICPSudo.get_param('res.config.settings.tax_retencion_id', default=False)
        tax_perception_id = ICPSudo.get_param('res.config.settings.tax_perception_id', default=False)
        
        # Convierte a entero si no es False, de lo contrario usa False
        res.update({
            'tax_retencion_id': int(tax_retencion_id) if tax_retencion_id and tax_retencion_id.isdigit() else False,
            'tax_perception_id': int(tax_perception_id) if tax_perception_id and tax_perception_id.isdigit() else False,
        })
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param('res.config.settings.tax_retencion_id', str(self.tax_retencion_id.id) if self.tax_retencion_id else '')
        ICPSudo.set_param('res.config.settings.tax_perception_id', str(self.tax_perception_id.id) if self.tax_perception_id else '')
