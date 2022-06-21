import base64
import pytz
import logging
from odoo import fields, models, _
from dateutil import parser
from datetime import datetime
from lxml import objectify
from odoo.exceptions import UserError, ValidationError


_logger = logging.getLogger(__name__)


def convert(obj, conversion=None):
    if conversion:
        return conversion(obj.text)
    if isinstance(obj, objectify.StringElement):
        return str(obj)
    if isinstance(obj, objectify.IntElement):
        return int(obj)
    if isinstance(obj, objectify.FloatElement):
        return float(obj)
    raise u"Tipo não implementado %s" % str(type(obj))


def get(obj, path, conversion=None):
    paths = path.split(".")
    index = 0
    for item in paths:
        if not item:
            continue
        if hasattr(obj, item):
            obj = obj[item]
            index += 1
        else:
            return None
    if len(paths) == index:
        return convert(obj, conversion=conversion)
    return None


def remove_none_values(dict):
    res = {}
    res.update({k: v for k, v in dict.items() if v})
    return res


def cnpj_cpf_format(cnpj_cpf):
    if len(cnpj_cpf) == 14:
        cnpj_cpf = (cnpj_cpf[0:2] + '.' + cnpj_cpf[2:5] +
                    '.' + cnpj_cpf[5:8] +
                    '/' + cnpj_cpf[8:12] +
                    '-' + cnpj_cpf[12:14])
    else:
        cnpj_cpf = (cnpj_cpf[0:3] + '.' + cnpj_cpf[3:6] +
                    '.' + cnpj_cpf[6:9] + '-' + cnpj_cpf[9:11])
    return cnpj_cpf


def format_ncm(ncm):
    if len(ncm) == 4:
        ncm = ncm[:2] + '.' + ncm[2:4]
    elif len(ncm) == 6:
        ncm = ncm[:4] + '.' + ncm[4:6]
    else:
        ncm = ncm[:4] + '.' + ncm[4:6] + '.' + ncm[6:8]

    return ncm


class AccountMove(models.Model):
    _inherit = 'account.move'

    """ ================================================
                        Validado    
    ================================================="""

    def import_nfe(self, company_id, nfe, xml):
        _logger.info(["import_nfe"])

        if self.search([('document_key', '=', nfe.protNFe.infProt.chNFe.text)]):
            raise UserError('Documento Eletrônico já importado!')

        invoice = {
            # Campos obrigatórios
            "invoice_date": nfe.NFe.infNFe.ide.dhEmi.text,
            "date": nfe.NFe.infNFe.ide.dhEmi.text,
            "company_id": company_id.id,
            "currency_id": company_id.currency_id.id,
            "journal_id": self.env["account.journal"].search([("type","=","purchase")], limit=1).id,
            "move_type": "in_invoice",
            "state": "draft",
            "state_edoc": "em_digitacao",

            # Não obrigatórios
            "document_type_id": company_id.document_type_id.id,
            "document_number": nfe.NFe.infNFe.ide.nNF.text,
            "document_key": nfe.protNFe.infProt.chNFe.text,
            "document_serie": nfe.NFe.infNFe.ide.serie.text,
        }

        invoice.update(self._get_company_invoice(nfe))
        invoice.update(self.get_partner_nfe(nfe))

        _logger.info(["Criando Fatura"])
        invoice = self.create(invoice)

        xml_file_vals = {
            "name": f"NFe-{nfe.protNFe.infProt.chNFe.text}.xml",
            "datas": xml
        }
        _logger.info(["Criando Att Xml"])
        xml_file = self.env["ir.attachment"].create(xml_file_vals)

        vals_event = {
            "company_id": company_id.id,
            "document_id": invoice.fiscal_document_id.id,
            "document_type_id": company_id.document_type_id.id,
            "document_number": nfe.NFe.infNFe.ide.nNF.text,
            "document_serie_id": self.env["l10n_br_fiscal.document.serie"].search([('code','=','1')], limit=1).id,
            "partner_id": invoice.partner_id.id or False,
            "protocol_number": nfe.protNFe.infProt.nProt.text,
            "file_response_id": xml_file.id,
            "file_request_id": xml_file.id
        }
        _logger.info(["Criando Evento de Autorização"])
        authorization_event = self.env["l10n_br_fiscal.event"].create(vals_event)

        update_invoice = {
            "authorization_event_id": authorization_event.id
        }
        _logger.info(["Atualizando Fatura"])
        invoice.update(update_invoice)

        return invoice

    def _get_company_invoice(self, nfe):
        dest_cnpj_cpf = cnpj_cpf_format(str(nfe.NFe.infNFe.dest.CNPJ.text).zfill(14))
        company = self.env['res.company'].sudo().search([('partner_id.cnpj_cpf', '=', dest_cnpj_cpf)])

        if not company: 
            raise UserError("XML não destinado nem emitido por esta empresa.")
        return dict(company_id=company.id,)

    def get_partner_nfe(self, nfe):
        cnpj_cpf = cnpj_cpf_format(str(nfe.NFe.infNFe.emit.CNPJ.text).zfill(14))
        partner_id = self.env['res.partner'].search([('cnpj_cpf', '=', cnpj_cpf)], limit=1)        
        if not partner_id:
            raise ValidationError(_("Parceiro não cadastrado"))
        
        return dict(partner_id=partner_id.id)


    """ ================================================
                    TODO Não Validado    
    ================================================="""

    def create_invoice_item(self, item, company_id, partner_id):
        codigo = get(item.prod, 'cProd', str)

        seller_id = self.env['product.supplierinfo'].search([
            ('name', '=', partner_id),
            ('product_code', '=', codigo),
            ('product_id.active', '=', True)])

        product = None
        if seller_id:
            product = seller_id.product_id
            if len(product) > 1:
                message = '\n'.join(["Produto: %s - %s" % (x.default_code or '', x.name) for x in product])
                raise UserError("Existem produtos duplicados com mesma codificação, corrija-os antes de prosseguir:\n%s" % message)

        if not product and item.prod.cEAN and \
           str(item.prod.cEAN) != 'SEM GTIN':
            product = self.env['product.product'].search(
                [('barcode', '=', item.prod.cEAN)], limit=1)

        uom_id = self.env['uom.uom'].search([
            ('name', '=', str(item.prod.uCom))], limit=1).id

        if not uom_id:
            uom_id = product and product.uom_id.id or False
        product_id = product and product.id or False

        quantidade = item.prod.qCom
        preco_unitario = item.prod.vUnCom
        valor_bruto = item.prod.vProd
        desconto = 0
        if hasattr(item.prod, 'vDesc'):
            desconto = item.prod.vDesc
        seguro = 0
        if hasattr(item.prod, 'vSeg'):
            seguro = item.prod.vSeg
        frete = 0
        if hasattr(item.prod, 'vFrete'):
            frete = item.prod.vFrete
        outras_despesas = 0
        if hasattr(item.prod, 'vOutro'):
            outras_despesas = item.prod.vOutro
        indicador_total = str(item.prod.indTot)
        cfop = item.prod.CFOP
        ncm = item.prod.NCM
        cest = get(item, 'item.prod.CEST')
        nItemPed = get(item, 'prod.nItemPed')

        invoice_eletronic_Item = {
            'product_id': product_id, 'uom_id': uom_id,
            'quantidade': quantidade, 'preco_unitario': preco_unitario,
            'valor_bruto': valor_bruto, 'desconto': desconto, 'seguro': seguro,
            'frete': frete, 'outras_despesas': outras_despesas,
            'valor_liquido': valor_bruto - desconto + frete + seguro + outras_despesas,
            'indicador_total': indicador_total, 'unidade_medida': str(item.prod.uCom),
            'cfop': cfop, 'ncm': ncm, 'product_ean': item.prod.cEAN,
            'product_cprod': codigo, 'product_xprod': item.prod.xProd,
            'cest': cest, 'item_pedido_compra': nItemPed,
            'company_id': company_id.id,
        }
        if hasattr(item.prod, 'DI'):
            di_ids = []
            for di in item.prod.DI:
                di_ids.append(self._get_di(item.prod.DI))
            invoice_eletronic_Item.update({'import_declaration_ids': di_ids})

        #return self.env['eletronic.document.line'].create(
        #    invoice_eletronic_Item)

   
    def get_items(self, nfe, company_id, partner_id, supplier):
        items = []
        for det in nfe.NFe.infNFe.det:
            item = self.create_invoice_item(
                det, company_id, partner_id, supplier)
            items.append((4, item.id if item else False, False))
        return {'document_line_ids': items}

    


