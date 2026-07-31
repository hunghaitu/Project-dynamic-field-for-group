from odoo import models, fields


class ProjectTaskCategory(models.Model):
    _name = "project.task.category"
    _description = "Task Category"
    _order = "sequence, id"

    name = fields.Char(
        string="Task Category Name",
        required=True,
        translate=True,
        help="The name of the task category (e.g., Core Work)"
    )
    code = fields.Char(
        string="Task Category Code",
        required=True, copy=False, )
    active = fields.Boolean(string="Active", default=True)
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Determine the display order of categories"
    )
    description = fields.Text(
        string="Description / Note", copy=False,
        help="Detailed description of the task category"
    )

    _unique_code = models.Constraint(
        "UNIQUE(code)",
        "The Task Category Code must be unique!"
    )

    def copy_data(self, default=None):
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
