import base64
import re
import logging

from odoo import models, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)

try:
    from pytrustnfe.nfe import consulta_cadastro
    from pytrustnfe.certificado import Certificado
except ImportError:
    _logger.error(
        'pytrustnfe3 not installed', exc_info=True)


class Partner(models.Model):
    _name = "res.partner"
    _inherit = [_name, "l10n_br_base.party.mixin"]

    def action_check_sefaz(self):
        if self.cnpj_cpf and self.state_id:
            if self.state_id.code == 'AL':
                raise UserError(_(u'Alagoas não tem esse serviço'))
            if self.state_id.code == 'RJ':
                raise UserError(_(
                    u'Rio de Janeiro não tem esse serviço'))
            company = self.env.company
            if not company.certificate_nfe_id:
                raise UserError(_("Certificate not found"))
            cert = company.with_context(
                {'bin_size': False}).certificate_nfe_id.file
            cert_pfx = base64.decodebytes(cert)
            certificado = Certificado(
                cert_pfx, company.certificate_nfe_id.password)
            cnpj = re.sub('[^0-9]', '', self.cnpj_cpf)
            obj = {'cnpj': cnpj, 'estado': self.state_id.code}
            resposta = consulta_cadastro(certificado, obj=obj, ambiente=1,
                                         estado=self.state_id.ibge_code)

            info = resposta['object'].getchildren()[0]
            info = info.infCons
            if info.cStat == 111 or info.cStat == 112:
                if not self.inscr_est:
                    self.inscr_est = info.infCad.IE.text
                if not self.cnpj_cpf:
                    self.cnpj_cpf = info.infCad.CNPJ.text

                def get_value(obj, prop):
                    if prop not in dir(obj):
                        return None
                    return getattr(obj, prop)

                main_cnae = 'l10n_br_fiscal.cnae_' + \
                    str(get_value(info.infCad, 'CNAE'))
                search_cnae = self.env['l10n_br_fiscal.cnae'].search(
                    [('id', '=', self.env.ref(main_cnae).id)]
                )
                if search_cnae:
                    self.cnae_main_id = search_cnae.id
                else:
                    _logger.warning("CNAE Não localizado")
                self.legal_name = get_value(info.infCad, 'xNome')
                if "ender" not in dir(info.infCad):
                    return
                cep = get_value(info.infCad.ender, 'CEP') or ''
                self.zip = str(cep).zfill(8) if cep else ''
                self.street_name = get_value(info.infCad.ender, 'xLgr')
                self.street_number = get_value(info.infCad.ender, 'nro')
                self.street2 = get_value(info.infCad.ender, 'xCpl')
                self.district = get_value(
                    info.infCad.ender, 'xBairro')
                cMun = get_value(info.infCad.ender, 'cMun')
                xMun = get_value(info.infCad.ender, 'xMun')
                city = None
                if cMun:
                    city = self.env['res.city'].search(
                        [('ibge_code', '=', str(cMun)[2:]),
                         ('state_id', '=', self.state_id.id)])
                if not city and xMun:
                    city = self.env['res.city'].search(
                        [('name', 'ilike', xMun),
                         ('state_id', '=', self.state_id.id)])
                if city:
                    self.city = xMun
                    self.city_id = city.id
            else:
                msg = "%s - %s" % (info.cStat, info.xMotivo)
                raise UserError(msg)
        else:
            raise UserError(
                _('Selecione o Estado e digite o CNPJ para consultar'))
