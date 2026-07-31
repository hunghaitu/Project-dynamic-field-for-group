from odoo import models, fields


class OvertimeCategory(models.Model):
    _name = "overtime.category"
    _description = "Overtime Category"
    _order = "id"

    name = fields.Char(
        string="OT Category Name",
        required=True,
        translate=True,
        help="Name of the overtime category (e.g., OT Weekly)"
    )
    code = fields.Char(
        string="OT Category Code",
        required=True,
        copy=False,
        help="Unique code for this overtime category (e.g., OTW)"
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    description = fields.Text(
        string="Description / Note",
        copy=False
    )

    _unique_ot_category_code = models.Constraint(
        "UNIQUE(code)",
        "Overtime Category Code must be unique!"
    )

    def copy_data(self, default=None):
        """Prepare copy data with unique code generation using suffix tags."""
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
