# Copyright (C) 2009  Renato Lima - Akretion
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import _, fields, models
from odoo.exceptions import UserError


class StockInvoiceOnshipping(models.TransientModel):
    _inherit = "stock.invoice.onshipping"

    fiscal_operation_journal = fields.Boolean(
        string="Account Jornal from Fiscal Operation",
        default=True,
    )

    group = fields.Selection(
        selection_add=[("fiscal_operation", "Fiscal Operation")],
        ondelete={"fiscal_operation": "set default"},
    )

    def _get_journal(self):
        """
        Get the journal depending on the journal_type
        :return: account.journal recordset
        """
        self.ensure_one()
        if self.fiscal_operation_journal:
            pickings = self._load_pickings()
            picking = fields.first(pickings)
            journal = picking.fiscal_operation_id.journal_id
            if not journal:
                raise UserError(
                    _(
                        "Invalid Journal! There is not journal defined"
                        " for this company: %s in fiscal operation: %s !"
                    )
                    % (picking.company_id.name, picking.fiscal_operation_id.name)
                )
        else:
            journal = super()._get_journal()
        return journal

    def _build_invoice_values_from_pickings(self, pickings):
        invoice, values = super()._build_invoice_values_from_pickings(pickings)
        pick = fields.first(pickings)
        fiscal_vals = pick._prepare_br_fiscal_dict()

        document_type = pick.company_id.document_type_id
        document_type_id = pick.company_id.document_type_id.id

        fiscal_vals["document_type_id"] = document_type_id

        document_serie = document_type.get_document_serie(
            pick.company_id, pick.fiscal_operation_id
        )
        if document_serie:
            fiscal_vals["document_serie_id"] = document_serie.id

        if pick.fiscal_operation_id and pick.fiscal_operation_id.journal_id:
            fiscal_vals["journal_id"] = pick.fiscal_operation_id.journal_id.id

        # Endereço de Entrega diferente do Endereço de Faturamento
        # so informado quando é diferente
        if fiscal_vals["partner_id"] != values["partner_id"]:
            values["partner_shipping_id"] = fiscal_vals["partner_id"]
        # Ser for feito o update como abaixo o campo
        # fiscal_operation_id vai vazio
        # fiscal_vals.update(values)
        values.update(fiscal_vals)

        return invoice, values

    def _get_invoice_line_values(self, moves, invoice_values, invoice):
        """
        Create invoice line values from given moves
        :param moves: stock.move
        :param invoice: account.invoice
        :return: dict
        """

        values = super()._get_invoice_line_values(moves, invoice_values, invoice)
        move = fields.first(moves)
        fiscal_values = move._prepare_br_fiscal_dict()

        # A Fatura não pode ser criada com os campos price_unit e fiscal_price
        # negativos, o metodo _prepare_br_fiscal_dict retorna o price_unit
        # negativo, por isso é preciso tira-lo antes do update, e no caso do
        # fiscal_price é feito um update para caso do valor ser diferente do
        # price_unit
        del fiscal_values["price_unit"]
        fiscal_values["fiscal_price"] = abs(fiscal_values.get("fiscal_price"))

        # Como é usada apenas uma move para chamar o _prepare_br_fiscal_dict
        # a quantidade/quantity do dicionario traz a quantidade referente a
        # apenas a essa linha por isso é removido aqui.
        del fiscal_values["quantity"]

        # Mesmo a quantidade estando errada por ser chamada apenas por uma move
        # no caso das stock.move agrupadas e os valores fiscais e de totais
        # retornados poderem estar errados ao criar o documento fiscal isso
        # será recalculado já com a quantidade correta.

        values.update(fiscal_values)

        # Assim nao entrava as taxas DEDUTIVEIS
        # values["tax_ids"] = [
        #     (
        #         6,
        #         0,
        #         self.env["l10n_br_fiscal.tax"]
        #         .browse(move.tax_id.ids)
        #         .account_taxes()
        #         .ids,
        #     )
        # ]

        # aqui passo as taxas dedutiveis
        type = "purchase"
        if move.fiscal_operation_id.fiscal_operation_type == 'in':
            type = "sale"
        tax_ids = move.fiscal_tax_ids.account_taxes(user_type=type).ids
        if move.fiscal_operation_id.deductible_taxes:
            tax_ids += move.fiscal_tax_ids.account_taxes(
                user_type=type, deductible=True
            ).ids

        values["tax_ids"] = [
            (
                6,
                0,
                tax_ids,
            )
        ]

        return values

    def _get_move_key(self, move):
        """
        Get the key based on the given move
        :param move: stock.move recordset
        :return: key
        """
        key = super()._get_move_key(move)
        if move.fiscal_operation_line_id:
            # Linhas de Operações Fiscais diferentes
            # não podem ser agrupadas
            if type(key) is tuple:
                key = key + (move.fiscal_operation_line_id,)
            else:
                # TODO - seria melhor identificar o TYPE para saber se
                #  o KEY realmente é um objeto nesse caso
                key = (key, move.fiscal_operation_line_id)

        return key

    def _search_document_related(self, invoice):
        pickings = self._load_pickings()
        picking = fields.first(pickings)
        if picking.fiscal_operation_id and picking.fiscal_operation_id.fiscal_type == "purchase_refund":
            reference = self.env['purchase.order'].search([('name','=',picking.group_id.name)])
            one_document = True
            for doc_referenced in reference.invoice_ids:
                if (doc_referenced.fiscal_operation_id.return_fiscal_operation_id == picking.fiscal_operation_id
                    and doc_referenced.document_type_id.code == "55"):
                    subsequent_documents = []
                    subsequent_documents.append(
                    (
                        0,
                        0,
                        {
                            "document_id": invoice.fiscal_document_id.id,
                            "document_related_id": doc_referenced.fiscal_document_id.id,
                            "document_type_id": doc_referenced.document_type_id.id,
                            "document_serie": doc_referenced.document_serie,
                            "document_number": doc_referenced.document_number,
                            "document_date": doc_referenced.document_date,
                            "document_key": doc_referenced.document_key,
                        },
                    )
                    )
                    # se existe mais de um documento fiscal para o pedido entao tem 
                    # que selecionar manualmente
                    if one_document:
                        invoice.write({"document_related_ids": subsequent_documents})
                    one_document = False

    # Usei esta funcao para corrigir quando tem Unidade Fiscal no item
    # e para carregar a conta que esta nos tributos
    def _create_invoice(self, invoice_values):
        """Override this method if you need to change any values of the
        invoice and the lines before the invoice creation
        :param invoice_values: dict with the invoice and its lines
        :return: invoice
        """
        
        for values in invoice_values['invoice_line_ids']:
            if len(values) == 3 and not 'product_id' in values[2]:
                continue
            product = self.env["product.product"].browse([values[2]['product_id']])
            if product and product.uot_id and product.uom_id != product.uot_id:
                values[2]["uot_id"] = product.uot_id.id
                values[2]["fiscal_price"] = values[2]['price_unit'] / (product.uot_factor or 1.0)
                values[2]["fiscal_quantity"] = values[2]['quantity'] * (product.uot_factor or 1.0)

        invoice = super()._create_invoice(invoice_values)

        for invoice_id in invoice:
            
            if invoice_id.fiscal_operation_id.fiscal_type == "purchase_refund":
                # buscando documento de referencia se existir
                self._search_document_related(invoice_id)

            # coloquei isso pq nao estava carregando o edoc_purpose
            if invoice_id.fiscal_operation_id:
                # coloquei as linhas abaixo copiadas do document.py do fiscal pq nao passava la
                invoice_id.operation_name = invoice_id.fiscal_operation_id.name
                invoice_id.comment_ids = invoice_id.fiscal_operation_id.comment_ids            
                invoice_id.fiscal_operation_type = invoice_id.fiscal_operation_id.fiscal_operation_type
                invoice_id.edoc_purpose = invoice_id.fiscal_operation_id.edoc_purpose

            # In the case of partial deliveries, recalculates the calculation
            # base and tax amounts
            for line in invoice_id.invoice_line_ids:
                line._onchange_fiscal_tax_ids()

        # Estava saindo com a Conta errada no line_ids
        for inv_line in invoice.line_ids:
            for tax in inv_line.tax_ids:
                for inv in invoice.line_ids:
                    if inv.name == tax.name:
                        for rep in tax.invoice_repartition_line_ids:
                            if rep.account_id and rep.account_id != inv.account_id:
                                inv.account_id = rep.account_id.id
        return invoice
