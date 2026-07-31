from odoo import models, fields


class ReworkReason(models.Model):
    _name = "rework.reason"
    _description = "Rework Reason"
    _order = "sequence, id"

    name = fields.Char(
        string="Rework Reason Name",
        required=True,
        translate=True,
    )
    code = fields.Char(
        string="Rework Reason Code",
        required=True,
        copy=False,
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
    )
    description = fields.Text(
        string="Description / Note",
        copy=False
    )

    _unique_rework_code = models.Constraint(
        "UNIQUE(code)",
        "Rework Reason Code must be unique!"
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
