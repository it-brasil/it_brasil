# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, format_date


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_post(self, invoice=False):
        result = super().action_post()
        recompute_payment_terms = False
        if self.document_number:
            for line in self.line_ids:
                if line.account_id.user_type_id.type in ('receivable', 'payable'):
                    if self.document_number not in line.name:
                        recompute_payment_terms = True
        if recompute_payment_terms:
            self._recompute_payment_terms_lines()
            #         if (line.name and not self.document_number in line.name
            #            and not line.nota_parcela in line.name):
            #            line.name = '%s - %s %s' %(self.document_number, line.nota_parcela, line.name)

            #         if (line.name and not self.document_number in line.name
            #            and line.nota_parcela in line.name):
            #            line.name = '%s - %s' %(self.document_number, line.name)

            #         if not line.name:
            #            line.name = '%s - %s' %(self.document_number, line.nota_parcela)
        return result


# NAO ESTOU USANDO ISTO ABAIXO , EXCLUIR A VIEW PRIMEIRO E TIRAR ISSO ?????????????????????
class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    # nota_parcela = fields.Char(
    #     String="Nota/Parcela",
    #     )

    def _gera_nota_parcela(self, vals):
        values = vals
        total = 0
        name = ""
        import pudb;pu.db
        account = self.env['account.account']
        for inv in values:
            if "account_id" in inv and inv.get("account_id"):
                acc = account.browse(inv.get('account_id'))
                if acc.user_type_id.type in ('receivable', 'payable'):
                    total += 1
        parc = 1
        for inv in values:
            if "account_id" in inv and inv.get("account_id"):
                acc = account.browse(inv.get('account_id'))
                if acc.user_type_id.type in ('receivable', 'payable'):
                    name = "%s/%s" %(str(parc).zfill(2),str(total).zfill(2))
                    inv["nota_parcela"] = name
                    if "name" not in vals:
                        inv["name"] = name
                    if "name" in vals and name not in vals.get('name'):
                        inv["name"] = name + ' ' + vals.get('name')                
                    if "name" in vals and not vals.get('name'):
                        inv["name"] = name
                    parc += 1
        return values

    @api.model_create_multi
    def create(self, vals_list):
        # nota_parc = ""
        # import pudb;pu.db
        # for vals in vals_list:
        #     if "nota_parcela" in vals:
        #         nota_parc = vals.get("nota_parcela")
        # if not nota_parc:
        #     vals_list = self._gera_nota_parcela(vals_list)

        invoice = super().create(vals_list)
        # for inv in invoice:
        #     if nota_parc and nota_parc not in inv.name:
        #         if inv.name:
        #             inv.name = nota_parc + '(%s)' %(inv.name)
        #         else:
        #             inv.name = nota_parc

        return invoice