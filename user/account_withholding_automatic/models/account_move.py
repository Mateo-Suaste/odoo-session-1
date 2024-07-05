from odoo import fields, api, exceptions, models

class AccountMove (models.Model):
    _inherit = "account.move"

    def get_tax_line_ret(self):
        alicuot_ret = self.env["arba.alicuot"].sudo().search([('regimen', '=', 'retencion'),
                                                              ('partner_id', '=', self.partner_id.id)])
        

        amount_untaxed = self.amount_untaxed
        amount_total = self.amount_total
        
        if not alicuot_ret:
            return False
        
        if alicuot_ret.witholding_amount_type == "total_amount":
            tax_line = {
                'tax_id': alicuot_ret.tax_id.id,
                'amount': (amount_total * alicuot_ret.alicuot_retencion) / 100
            }
            return tax_line
        
        tax_line = {
            'tax_id': alicuot_ret.tax_id.id,
            'amount': (amount_untaxed * alicuot_ret.alicuot_retencion) / 100
        }
        return tax_line


    def action_register_payment(self):
         result = super(AccountMove, self).action_register_payment()

         tax_line = self.get_tax_line_ret()

         if not tax_line or self.move_type != "in_invoice":
             return result
         
         # Fetch the current payment register form view
         view_id = self.env.ref('account.view_account_payment_register_form').id
        # Open the payment register form view to get the record ID
         context = result.get('context', {})
         payment_register = self.env['account.payment.register'].with_context(context).search([], limit=1)

         

         # Eliminar las líneas existentes
         existing_withholding_lines = self.env['l10n_ar.payment.register.withholding'].sudo().search([
            ('payment_register_id', '=', payment_register.id)
         ])
         
         if existing_withholding_lines:
            existing_withholding_lines.unlink()

        # Add the tax withholding to the related model
         self.env['l10n_ar.payment.register.withholding'].sudo().create({
            'payment_register_id': payment_register.id,
            'tax_id': tax_line['tax_id'],
            'amount': tax_line['amount'],
            'base_amount': 0
         })

         print(tax_line)

         result.update({
            'res_id': payment_register.id,
            'view_id': view_id,
            'context': context,
         })

         return result