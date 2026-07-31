from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    cluster_id = fields.Many2one("hr.cluster", string="Cluster", required=True, tracking=True)
    group_id = fields.Many2one("hr.group", string="Group", required=True, tracking=True)
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



    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        groups = projects.filtered(lambda p: p.group_id).mapped("group_id")
        if groups:
            self.env["dynamic.timesheet.layout.config"]._update_group_views(groups)
        return projects

    def write(self, vals):
        res = super().write(vals)
        if "group_id" in vals:
            groups = self.filtered(lambda p: p.group_id).mapped("group_id")
            if groups:
                self.env["dynamic.timesheet.layout.config"]._update_group_views(groups)
        return res
