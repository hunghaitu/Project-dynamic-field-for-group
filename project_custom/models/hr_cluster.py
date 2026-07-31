from odoo import models, fields, api


class HrCluster(models.Model):
    _name = "hr.cluster"
    _description = "Hr Cluster"
    _order = "name"

    name = fields.Char(string="Cluster Name", required=True)
    code = fields.Char(string="Cluster Code", required=True, copy=False, )
    manager_id = fields.Many2one("hr.employee", string="Manager")
    group_ids = fields.One2many("hr.group", "cluster_id", string="Groups")
    description = fields.Text("Description/ Note")
    active = fields.Boolean(
        string="Active",
        default=True
    )
    project_ids = fields.One2many(
        "project.project",
        "cluster_id",
        string="Projects"
    )
    group_count = fields.Integer(
        string="Groups",
        compute="_compute_group_count",
        help="Total number of groups inside this cluster."
    )
    project_count = fields.Integer(
        string="Projects",
        compute="_compute_project_count",
        help="Total number of projects inside this cluster."
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

    @api.depends("group_ids")
    def _compute_group_count(self):
        """Compute the total number of groups linked to this cluster."""
        for cluster in self:
            cluster.group_count = len(cluster.group_ids)

    @api.depends("project_ids")
    def _compute_project_count(self):
        """Compute the total number of projects linked to this cluster."""
        for cluster in self:
            cluster.project_count = len(cluster.project_ids)

    def action_view_linked_groups(self):
        """Open list view of groups filtered by this cluster."""
        self.ensure_one()
        return {
            "name": "Groups",
            "type": "ir.actions.act_window",
            "res_model": "hr.group",
            "view_mode": "list,form",
            "domain": [("cluster_id", "=", self.id)],
            "context": {"default_cluster_id": self.id},
        }

    def action_view_linked_projects(self):
        """Open list view of projects filtered by this cluster."""
        self.ensure_one()
        return {
            "name": "Projects",
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "view_mode": "list,form",
            "domain": [("cluster_id", "=", self.id)],
            "context": {"default_cluster_id": self.id},
        }
