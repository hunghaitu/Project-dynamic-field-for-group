from odoo import models, fields


class FlexReason(models.Model):
    _name = "flex.reason"
    _description = "Flex Reason"
    _order = "id"

    name = fields.Char(
        string="Flex Reason Name",
        required=True,
        translate=True,
        help="Name of the flex reason (e.g., Work Shortage)"
    )
    code = fields.Char(
        string="Flex Reason Code",
        required=True,
        copy=False,
        help="Unique code for this flex reason, must be unique."
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    description = fields.Text(
        string="Description / Note",
        copy=False
    )

    _unique_flex_reason_code = models.Constraint(
        "UNIQUE(code)",
        "Flex Reason Code must be unique!"
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
