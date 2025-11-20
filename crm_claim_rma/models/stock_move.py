# -*- coding: utf-8 -*-
# © 2015 Eezee-It, MONK Software, Vauxoo
# © 2013 Camptocamp
# © 2009-2013 Akretion,
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models


class StockMove(models.Model):

    _name = 'stock.move'
    _inherit = ['stock.move', 'mail.thread']

    @api.model
    def create(self, vals):
        """ In case of a wrong picking out,
        We need to create a new stock_move in a picking already open.
        To avoid having to confirm the stock_move, we override the create and
        confirm it at the creation only for this case.
        """
        move = super(StockMove, self).create(vals)
        if vals.get('picking_id'):
            picking = self.env['stock.picking'].browse(vals['picking_id'])
            if picking.claim_id and picking.picking_type_id.code == 'incoming':
                move.write({'state': 'confirmed'})
        return move

    def _action_explode(self, cr, uid, move, context=None):
        """Override to prevent kit BoM explosion for RMA repair pickings.
        
        When creating pickings from RMA claims for repair purposes, we want
        to keep kit products as kits rather than exploding them into their
        components. This method checks if the move is related to an RMA claim
        and if so, skips the BoM explosion for kit products.
        
        This method uses the old API style (cr, uid) to match Odoo 9.0's
        core implementation signature.
        
        :param cr: database cursor
        :param uid: user id
        :param move: stock.move record
        :param context: context dictionary
        :return: list of moves (original move if RMA-related kit, otherwise exploded)
        """
        context = context or {}
        # Check if this move is part of an RMA claim picking
        picking_obj = self.pool.get('stock.picking')
        if move.picking_id:
            picking = picking_obj.browse(cr, uid, move.picking_id.id, context=context)
            if picking.claim_id:
                # For RMA repairs, we want to keep kit products as kits
                # Check if product has a phantom BoM (kit product)
                if move.product_id:
                    try:
                        bom_obj = self.pool.get('mrp.bom')
                        if bom_obj:
                            bom_ids = bom_obj.search(
                                cr, uid,
                                [('product_id', '=', move.product_id.id),
                                 ('type', '=', 'phantom')],
                                limit=1,
                                context=context
                            )
                            # If it's a kit product in an RMA picking, don't explode it
                            if bom_ids:
                                return [move]
                    except:
                        # If mrp.bom is not available, continue with standard behavior
                        pass
        # For non-RMA moves or non-kit products, use standard behavior
        return super(StockMove, self)._action_explode(cr, uid, move, context=context)
