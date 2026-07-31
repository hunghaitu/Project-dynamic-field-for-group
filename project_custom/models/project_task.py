from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = "project.task"

    department_id = fields.Many2one("hr.department", "Department")
    code = fields.Char('Project ID', required=True, copy=False, )
    _unique_project_code = models.Constraint(
        "UNIQUE(code)",
        "Project Code must be unique!"
    )

    def copy_data(self, default=None):
        """Handle record duplication by appending a unique copy suffix."""
        default = dict(default or {})
        vals_list = super().copy_data(default)

        for vals in vals_list:
            if "code" not in vals or not vals["code"]:
                new_code = f"{self.code}_copy"
                count = 1
                while self.search_count([("code", "=", new_code)]):
                    new_code = f"{self.code}_copy_{count}"
                    count += 1
                vals["code"] = new_code

            if "name" not in vals:
                vals["name"] = f"{self.name} (Copy)"

        return vals_list
