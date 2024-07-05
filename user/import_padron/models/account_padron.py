from odoo import fields, models, exceptions, api
from datetime import date
from dateutil.relativedelta import relativedelta

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

    @api.model
    def create(self, vals):
        try:
            ##obtener los valores del padron
            company_id = vals.get("company_id")
            percent = vals.get("percent")
            date_from = vals.get("date_from")
            date_to = vals.get("date_to")
            regimen = vals.get("regimen")
            cuit = vals.get("cuit")

            ##obtener impuesto de las configuraciones
            ICPSudo = self.env['ir.config_parameter'].sudo()
            tax_retencion_id = ICPSudo.get_param('res.config.settings.tax_retencion_id', default=False)
            tax_perception_id = ICPSudo.get_param('res.config.settings.tax_perception_id', default=False)
            print(tax_perception_id, tax_retencion_id)

            ##Obtener cliente
            partner = self.env["res.partner"].sudo().search([('vat', '=', cuit)])

            if not partner:
                return super().create(vals)

            ##Obtener el valor de la configuracion de impuestos
            tax_retencion = self.env['account.tax'].browse(int(tax_retencion_id)) if tax_retencion_id else False
            tax_perception = self.env['account.tax'].browse(int(tax_perception_id)) if tax_perception_id else False

            if tax_perception_id is False or tax_retencion_id is False:
                raise exceptions.UserError("Configure los Impuestos de retencion o percepcion")
            
            ##Verificar que la alicuota no este repetida
            alicuot_exist = self.env['arba.alicuot'].sudo().search([('partner_id', '=', partner.id),
                                                                     ('date_from', '=', date_from),
                                                                     ('regimen', '=', regimen)])
            
            if alicuot_exist:
                return super().create(vals)

            #Crea diccionario de valores 
            vals_alicuot = {
                "from_padron": True,
                "company_id" : company_id,
                "witholding_amount_type" : "untaxed_amount",
                "date_from" : date_from,
                "date_to" : date_to,
                "tax_id": tax_perception.id if regimen == "percepcion" else tax_retencion.id,
                "alicuot_perception": percent if regimen == "percepcion" else 0.00,
                "alicuot_retencion": percent if regimen == "retencion" else 0.00,
                "partner_id" : partner.id,
                "regimen" : regimen
            }
            self.env["arba.alicuot"].create(vals_alicuot)

            return super().create(vals)

        except Exception as error:
            raise exceptions.UserError(f"Ocurrió un error: {str(error)}")
        
    def _delete_old_padron_alicuots(self):
        # Obtener la fecha del mes pasado
        last_month_date = date.today() - relativedelta(months=1)

        # Buscar registros de padron y alícuotas correspondientes al mes pasado
        old_padron = self.env["account.padron"].search([
            ('date_from', '>=', last_month_date.replace(day=1)),
            ('date_from', '<', date.today().replace(day=1))
        ])

        print("old_padron")
        print("Holas")
        '''old_alicuots = self.env["arba.alicuot"].search([
            ('date_from', '>=', last_month_date.replace(day=1)),
            ('date_from', '<', date.today().replace(day=1))
        ])'''

        print(old_padron['cuit'])

        # Eliminar los registros encontrados
        if old_padron:
            old_padron.unlink()
        '''if old_alicuots:
            old_alicuots.unlink()
'''

        return True
