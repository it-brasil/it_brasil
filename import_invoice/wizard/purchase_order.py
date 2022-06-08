import logging
import base64
import xml.etree.ElementTree as ET
from odoo import fields, models, _
from odoo.exceptions import UserError 

_logger = logging.getLogger(__name__)


class PurchaseOrderWizard(models.TransientModel):
    _name = "purchase.order.wizard"

    xml_invoice = fields.Binary(required=True)

    def import_invoice(self):
        base = base64.b64decode(self.xml_invoice).decode('UTF-8')
        root =  ET.ElementTree(ET.fromstring(base)).getroot()
        cnpj_emit = root.find(".//{http://www.portalfiscal.inf.br/nfe}emit/{http://www.portalfiscal.inf.br/nfe}CNPJ").text
        
        purchase = self.env["purchase.order"].browse(self._context.get("active_id"))
        cnpj_fornecedor = self.clear_cnpj(purchase.partner_id.cnpj_cpf) if purchase.partner_id.cnpj_cpf else False
        cnpj_xml = self.clear_cnpj(cnpj_emit)

        if cnpj_fornecedor != cnpj_xml:
            raise UserError(_("O CNPJ do emitente não é igual ao CNPJ do parceiro do pedido de compras"))

        itens =  {}
        search_itens = ["nNF", "chNFe","serie","nProt","finNFe", "dhRecbto","dhEmi"]
        
        for item in search_itens:
            src = root.find(".//{http://www.portalfiscal.inf.br/nfe}"+ item).text
            if item in ["dhRecbto","dhEmi"]:
                src = src.replace("T"," ").replace("-03:00","")
            itens[item] = src
        
        _logger.info(["[DEBUG]", itens])

        vals = {
            "document_number": itens["nNF"],
            "document_key": itens["chNFe"],
            "document_serie": itens["serie"],
            "authorization_protocol": itens["nProt"],
            "invoice_date": itens["dhEmi"],
            "date": itens["dhEmi"],
            "authorization_date": itens["dhRecbto"],
            "edoc_purpose": itens["finNFe"],
        } 
        
        invoice = purchase.action_create_invoice()
        self.env["account.move"].browse(invoice).write(vals)

    def clear_cnpj(self, cnpj):
        return cnpj.replace(".","").replace("/","").replace("-","")

    
