from odoo import models, fields, api, exceptions
from datetime import date
import base64
import pandas as pd
import io

class AccountImportPadron(models.Model):
    _name = "account.import.padron"
    _description = "Model of the import taxs padron"

    tax_prefix = fields.Selection(
        string="Prefijo Fiscal",
        copy=False,
        selection=[("RetIIBB", "RetIIBB"), ("PerIIBB", "PerIIBB")]
    )

    imported = fields.Boolean()
    line_limit = fields.Integer(default=500)
    company_id = fields.Many2one("res.company", string="Empresa")
    lines_count = fields.Integer(readonly=True, copy=False)
    update_count = fields.Integer(readonly=True, copy=False)
    create_count = fields.Integer(readonly=True, copy=False)
    padron_file = fields.Binary(copy=False)
    pre_processed = fields.Boolean(default=False)
    file_name = fields.Char(copy=False)
    create_date = fields.Date(default=date.today(), copy=False, readonly=True)
    padron_lines = fields.Text(readonly=True )



    @api.depends("padron_file")
    def action_compute_padron_lines(self):  
        for record in self:
        
            if record.padron_file:

                if not record.file_name.lower().endswith('.txt'):
                    raise exceptions.UserError("El archivo es invalido")

                file_data = base64.b64decode(record.padron_file).decode('utf-8')
                    
                df_padron = pd.read_csv(io.StringIO(file_data), sep=';', header=None)

                if df_padron.shape[1] != 9:
                    raise exceptions.UserError("El archivo es invalido")
                    
                names_of_columns =["Regimen",
                                "Fecha de Publicacion",
                                "Desde",
                                "Hasta",
                                "CUIT",
                                "T. de contribuyente",
                                "M. Sujeto",
                                "Ma.cambio de Alicuota",
                                "Porcentaje"]
                    
                df_padron.columns = names_of_columns

                df_padron["CUIT"] = df_padron["CUIT"].astype(str)

                validation = (df_padron["CUIT"].str.len() > 12) | (df_padron["CUIT"].str.len() < 11)

                if not validation.any:
                    raise exceptions.UserError("Verifique que el formato de identificacion sea el correcto")
                    
                df_padron["Fecha de Publicacion"] = pd.to_datetime(df_padron["Fecha de Publicacion"],
                                                                    format='%d%m%Y').dt.strftime('%Y-%m-%d')
                    
                df_padron["Desde"] = pd.to_datetime(df_padron["Desde"],
                                                                    format='%d%m%Y').dt.strftime('%Y-%m-%d')
                    
                df_padron["Hasta"] = pd.to_datetime(df_padron["Hasta"],
                                                                    format='%d%m%Y').dt.strftime('%Y-%m-%d')
                    
                pd.set_option("display.max_columns", None)
                pd.set_option('display.max_colwidth', 47)
                pd.set_option("display.width", None)
                pd.set_option("display.colheader_justify", "left")

                df_padron = df_padron.reset_index(drop=True)

                record.padron_lines = df_padron.to_csv(index=False, sep=";")
                record.pre_processed = True

    def action_import_padron(self):
        self.padron_lines = self.padron_lines
        if not self.padron_lines:
            raise exceptions.UserError("No hay datos preprocesados para importar.")

        padron_lines = io.StringIO(self.padron_lines)
        df_padron = pd.read_csv(padron_lines, sep=';')
        df_padron["CUIT"] = df_padron["CUIT"].astype(str)

        # Obtener todos los contactos con el tipo de responsabilidad "IVA Responsable Inscripto"
        partners = self.env['res.partner'].search([
            ('l10n_ar_afip_responsibility_type_id.name', '=', 'IVA Responsable Inscripto')
        ])

        partner_cuits = pd.DataFrame(partners.mapped('vat'), columns=['CUIT'])
        partner_cuits["CUIT"] = partner_cuits["CUIT"].astype(str)

        matched_cuits = df_padron.merge(partner_cuits, on="CUIT", how="inner")

        # Actualizar los contadores
        self.lines_count = len(matched_cuits)
        self.update_count = len(matched_cuits)
        self.create_count = len(df_padron) - len(matched_cuits)
