from odoo import models, fields


class HrGroup(models.Model):
    _name = "hr.group"
    _description = "Hr Group"
    _order = "name"

    name = fields.Char(string="Group Name", required=True)
    code = fields.Char(string="Group Code", )
    manager_id = fields.Many2one("hr.employee", string="Manager")
