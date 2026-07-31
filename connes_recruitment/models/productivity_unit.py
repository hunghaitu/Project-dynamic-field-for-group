from odoo import models, fields


class ProductivityUnit(models.Model):
    _name = "productivity.unit"
    _description = "Productivity Unit"
    _order = "sequence, id"

    name = fields.Char(
        string="Productivity Unit Name",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Productivity Unit Code",
        required=True,
        copy=False,
    )
    output_unit_id = fields.Many2one(
        "project.unit",
        string="Output Unit",
        ondelete="restrict",
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    formula_description = fields.Text(
        string="Formula Description / Calculation Note",
    )
    description = fields.Text(
        string="Description / Note",
        copy=False
    )

    _unique_productivity_code = models.Constraint(
        "UNIQUE(code)",
        "Productivity Unit Code must be unique!"
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
