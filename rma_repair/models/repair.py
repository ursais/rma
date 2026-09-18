# Copyright 2024 APSL-Nagarro Antoni Marroig
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class RepairOrder(models.Model):
    _inherit = "repair.order"

    rma_ids = fields.One2many(
        comodel_name="rma",
        inverse_name="repair_id",
        string="RMAs",
    )

    @api.model
    def default_get(self, fields_list):
        """Map default_repair_product_qty -> product_qty for RMA form defaults.

        Avoids using default_product_qty in context, which would also apply to
        stock.move and trigger _set_product_qty during End Repair.
        """
        res = super().default_get(fields_list)
        qty = self.env.context.get("default_repair_product_qty")
        if qty is not None and "product_qty" in fields_list:
            res["product_qty"] = qty
        return res

    def action_view_repair_rma(self):
        return {
            "name": f"RMAs - {self.name}",
            "type": "ir.actions.act_window",
            "view_mode": "list,form",
            "res_model": "rma",
            "domain": [("id", "in", self.rma_ids.ids)],
        }
