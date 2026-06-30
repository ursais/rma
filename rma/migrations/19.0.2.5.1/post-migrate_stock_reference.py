# Copyright 2026 Open Source Integrators
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    """Rename procurement group link to Odoo 19 stock references."""
    cr.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'rma' AND column_name = 'procurement_group_id'
        """
    )
    if not cr.fetchone():
        return
    cr.execute(
        "ALTER TABLE rma RENAME COLUMN procurement_group_id TO stock_reference_id"
    )
    cr.execute("UPDATE rma SET stock_reference_id = NULL")
