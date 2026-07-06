from odoo import models, fields


class ProjectTask(models.Model):
    _inherit = "project.task"

    timesheet_optional_fields = fields.Json(string="Timesheet Optional Fields", default="[]")
    department_id = fields.Many2one("hr.department", "Department")
