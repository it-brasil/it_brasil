import json
import re
import logging

import requests

from odoo import models, _
from odoo.exceptions import ValidationError, UserError


_logger = logging.getLogger(__name__)


class Partner(models.Model):
    _name = "res.partner"
    _inherit = [_name, "l10n_br_base.party.mixin"]

    def action_consult_cnpj(self):
        cnpjws_url = 'https://publica.cnpj.ws/cnpj/'
        if self.company_type == 'company':
            if self.cnpj_cpf:
                cnpj = re.sub('[^0-9]', '', self.cnpj_cpf)
                response = requests.get(cnpjws_url + cnpj)
                cnpjws_result = json.loads(response.text)
                if response.status_code == 200:
                    self.legal_name = cnpjws_result['razao_social']

                    cnpjws_estabelecimento = cnpjws_result['estabelecimento']
                    cnpjws_pais = cnpjws_result['estabelecimento']['pais']['comex_id']
                    cnpjws_estado = cnpjws_estabelecimento['estado']
                    cnpjws_cidade = cnpjws_estabelecimento['cidade']

                    search_country = self.env['res.country'].search(
                        [('siscomex_code', '=', cnpjws_pais)])
                    if search_country:
                        self.country_id = search_country.id

                    if cnpjws_estado['ibge_id']:
                        search_state = self.env['res.country.state'].search(
                            [('ibge_code', '=', cnpjws_estado['ibge_id'])])
                        if search_state:
                            self.state_id = search_state.id

                    if cnpjws_cidade:
                        self.city = cnpjws_cidade['nome']
                        search_city = self.env['res.city'].search(
                            [('ibge_code', '=', cnpjws_cidade['ibge_id'])])
                        if search_city:
                            self.city_id = search_city.id

                    self.zip = cnpjws_estabelecimento['cep']

                    if cnpjws_estabelecimento['tipo_logradouro']:
                        cnpj_t_logra = cnpjws_estabelecimento['tipo_logradouro']
                        cnpj_logra = cnpjws_estabelecimento['logradouro']

                        self.street_name = cnpj_t_logra + " " + cnpj_logra

                    self.street_number = cnpjws_estabelecimento['numero']

                    self.district = cnpjws_estabelecimento['bairro']
                    self.street2 = cnpjws_estabelecimento['complemento']
                else:
                    raise ValidationError(
                        "Erro: " + cnpjws_result['titulo'] + '\n' + cnpjws_result['detalhes'])
            else:
                raise UserError("Por favor, informe o CNPJ da empresa.")
        else:
            raise ValidationError(
                "Apenas contatos do tipo Empresa com CNPJ podem ser consultados.")
