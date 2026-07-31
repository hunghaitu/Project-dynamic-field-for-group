from odoo import models, fields


class ProjectUnit(models.Model):
    _name = "project.unit"
    _description = "Project Unit"
    _order = "sequence, id"

    name = fields.Char(
        string="Unit Name",
        required=True,
        translate=True,
        help="Tên đơn vị sản lượng, ví dụ Task, SKU, Ticket, Image."
    )
    code = fields.Char(
        string="Unit Code",
        required=True,
        copy=False,
        help="Mã đơn vị sản lượng, không được trùng lặp."
    )
    active = fields.Boolean(
        string="Active",
        default=True
    )
    sequence = fields.Integer(
        string="Sequence",
        default=10,
        help="Xác định thứ tự hiển thị của các đơn vị."
    )
    description = fields.Text(
        string="Description / Note",
        copy=False
    )

    _unique_unit_code = models.Constraint(
        "UNIQUE(code)",
        "Unit Code must be unique!"
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
