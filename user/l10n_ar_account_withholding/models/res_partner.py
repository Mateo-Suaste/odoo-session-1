from odoo import fields, models, exceptions, api
import pandas as pd
import io
import numpy as np

class ResPartner(models.Model):
    _inherit="res.partner"

    start_date = fields.Date(copy=False)
    last_update_padron = fields.Date(copy=False)
    imp_ganancias_padron = fields.Selection(
        selection=[("no inscripto", "No inscripto"),
                    ("activo", "Activo"),
                      ("excento", "Excento"),
                        ("no corresponde", "No corresponde") ]
    )

    default_regimen_ganancias_id = fields.Integer(copy=False)
    arba_alicuot_ids = fields.One2many("arba.alicuot", "partner_id", "Alícuotas PERC-RET")

    def action_update_ret_perc_from_padron (self):

        ##Buscar la importacion de padrones
        import_padron_ret = self.env["account.import.padron"].search([('tax_prefix', '=', 'RetIIBB')])
        import_padron_perc = self.env["account.import.padron"].search([('tax_prefix', '=', 'PerIIBB')])


        if not import_padron_perc or not import_padron_ret:
            raise exceptions.UserError("Ocurrio un Error: No se encontraron los padrones correspondientes")
        

        partner_cuit = self.vat

        padron_lines_ret = io.StringIO(import_padron_ret.padron_lines)
        df_padron_ret = pd.read_csv(padron_lines_ret, sep=';')
        df_padron_ret["CUIT"] = df_padron_ret["CUIT"].astype(str)

        padron_lines_perc = io.StringIO(import_padron_perc.padron_lines)
        df_padron_perc = pd.read_csv(padron_lines_perc, sep=';')
        df_padron_perc["CUIT"] = df_padron_perc["CUIT"].astype(str)

        alicuot_ret = df_padron_ret[df_padron_ret["CUIT"] == partner_cuit]
        alicuot_perc = df_padron_perc[df_padron_perc["CUIT"] == partner_cuit]

        if alicuot_ret.empty or alicuot_perc.empty:
          return {
              'type': 'ir.actions.client',
              'tag': 'display_notification',
              'params': {
                  'title': 'Error al importar alicuotas',
                  'message': 'No se encontraron registros coincidentes',
                  'type': 'error',
                  'sticky': False,
              }
        }

        ##Preparacion de los datos del padron de ret

        alicuot_ret = alicuot_ret.rename(columns={"Regimen": "regimen",
                                           "Fecha de Publicacion": "date_p",
                                           "Desde": "date_from",
                                           "Hasta" : "date_to",
                                           "CUIT" : "cuit",
                                           "T. de contribuyente" : "const_type",
                                           "M. Sujeto": "marc_subject",
                                           "Ma.cambio de Alicuota": "marc_change_alic",
                                           "Porcentaje": "percent"})
        
        alicuot_ret['regimen'] = 'retencion'
        alicuot_ret['marc_change_alic'] = np.where(alicuot_ret['marc_subject'] == 'S', 'si', 'no')
        alicuot_ret['percent'] = alicuot_ret['percent'].str.replace(',', '.').astype(float)
        alicuot_ret['tax'] = 'RetIBB'
        alicuot_ret['partner_updated'] = True
        alicuot_ret['from_padron_import'] = True
        alicuot_ret['padron_import_id'] = import_padron_ret.id
        alicuot_ret['company_id'] = import_padron_ret.company_id.id

        ##Preparacion de los datos del padron en perc
        
        alicuot_perc = alicuot_perc.rename(columns={"Regimen": "regimen",
                                           "Fecha de Publicacion": "date_p",
                                           "Desde": "date_from",
                                           "Hasta" : "date_to",
                                           "CUIT" : "cuit",
                                           "T. de contribuyente" : "const_type",
                                           "M. Sujeto": "marc_subject",
                                           "Ma.cambio de Alicuota": "marc_change_alic",
                                           "Porcentaje": "percent"})
        
        alicuot_perc['regimen'] = 'percepcion'
        alicuot_perc['marc_change_alic'] = np.where(alicuot_perc['marc_subject'] == 'S', 'si', 'no')
        alicuot_perc['percent'] = alicuot_perc['percent'].str.replace(',', '.').astype(float)
        alicuot_perc['tax'] = 'PercIIBB'
        alicuot_perc['partner_updated'] = True
        alicuot_perc['from_padron_import'] = True
        alicuot_perc['padron_import_id'] = import_padron_perc.id
        alicuot_perc['company_id'] = import_padron_perc.company_id.id


        dic_perc = alicuot_perc.to_dict('records')
        dic_ret = alicuot_ret.to_dict('records')

        self.env['account.padron'].sudo().create(dic_perc)
        self.env['account.padron'].sudo().create(dic_ret)

        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Importacion Completada',
                'message': 'Se importaron las alicuotas correspondientes',
                'type': 'success',
                'sticky': False,
            }
        }




         




