from odoo import models, fields, api


class HrGroup(models.Model):
    _name = "hr.group"
    _description = "Hr Group"
    _order = "name"

    name = fields.Char(string="Group Name", required=True)
    code = fields.Char(string="Group Code", required=True, copy=False, )
    cluster_id = fields.Many2one("hr.cluster", string="Cluster", required=True, ondelete="cascade")
    manager_id = fields.Many2one("hr.employee", string="Manager")
    active = fields.Boolean(
        string="Active",
        default=True
    )
    description = fields.Text("Description/ Note")
    project_ids = fields.One2many(
        "project.project",
        "group_id",
        string="Projects"
    )
    project_count = fields.Integer(
        string="Projects",
        compute="_compute_project_count",
        help="Total number of projects inside this group."
    )

    @api.depends("project_ids")
    def _compute_project_count(self):
        """Compute the total number of projects linked to this group."""
        for group in self:
            group.project_count = len(group.project_ids)

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

    def action_view_linked_projects(self):
        """Open list view of projects filtered by this group."""
        self.ensure_one()
        return {
            "name": "Projects",
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "view_mode": "list,form",
            "domain": [("group_id", "=", self.id)],
            "context": {"default_group_id": self.id},
        }
