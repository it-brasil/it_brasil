from odoo.addons.spec_driven_model.models import spec_models


class NFeLine(spec_models.StackedModel):
    _name = "l10n_br_fiscal.document.line"
    _inherit = ["l10n_br_fiscal.document.line", "nfe.40.det"]
    _stacked = "nfe.40.det"
    _field_prefix = "nfe40_"
    _schema_name = "nfe"
    _schema_version = "4.0.0"
    _odoo_module = "l10n_br_nfe"
    _spec_module = "odoo.addons.l10n_br_nfe_spec.models.v4_00.leiauteNFe"
    _spec_tab_name = "NFe"
    _stack_skip = "nfe40_det_infNFe_id"
    _stacking_points = {}
    _force_stack_paths = ("det.imposto",)


    def _export_fields(self, xsd_fields, class_obj, export_dict):
        if class_obj._name == "nfe.40.prod":
            if self.account_line_ids.move_id.move_type == "in_invoice":
                vals = {
                    "nfe40_DI_prod_id": self.id,
                    "nfe40_nDI" : self.number_di,
                    "nfe40_dDI" : self.date_registration,
                    "nfe40_xLocDesemb" : self.location,
                    "nfe40_UFDesemb" : self.state_id.code,
                    "nfe40_dDesemb": self.date_release,
                    "nfe40_tpViaTransp" : self.type_transportation,
                    "nfe40_vAFRMM" : self.afrmm_value,
                    "nfe40_tpIntermedio" : self.tpIntermedio,
                    "nfe40_CNPJ" : self.thirdparty_cnpj,
                    "nfe40_UFTerceiro" : self.thirdparty_state_id.code,
                    "nfe40_cExportador" : self.exporting_code,
                    "nfe40_adi": [
                        (
                            0,
                            0,
                            {
                                "nfe40_nAdicao": line.name,
                                "nfe40_nSeqAdic": line.sequence_di,
                                "nfe40_cFabricante": line.manufacturer_code,
                                "nfe40_vDescDI": line.amount_discount,
                                "nfe40_nDraw": line.drawback_number,
                            }
                        ) for line in self.di_ids
                    ]
                    }
                self.nfe40_DI = [(0,0, vals)]
        return super()._export_fields(xsd_fields, class_obj, export_dict)