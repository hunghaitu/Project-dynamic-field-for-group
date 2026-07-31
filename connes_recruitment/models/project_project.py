from odoo import models, fields, api


class ProjectProject(models.Model):
    _inherit = "project.project"

    cluster_id = fields.Many2one("cennos.cluster", string="Cluster", required=True, tracking=True)
    group_id = fields.Many2one("cennos.group", string="Group", required=True, tracking=True)
    code = fields.Char('Project ID', required=True, copy=False, )
    _unique_project_code = models.Constraint(
        "UNIQUE(code)",
        "Project Code must be unique!"
    )
    manager_ids = fields.Many2many("hr.employee", "project_employee_rel", "project_id", "employee_id", string="Project Manager")
    actual_start_date = fields.Date('Actual Start Date', tracking=True)
    actual_completion_date = fields.Date('Actual Completion Date', tracking=True)
    project_unit_id = fields.Many2one("project.unit", string="Unit", tracking=True)
    productivity_goal = fields.Float("Productivity Goal", tracking=True)
    productivity_unit_id = fields.Many2one("productivity.unit", string="Productivity Unit", tracking=True)
    estimated_productivity = fields.Float("Estimated Productivity", tracking=True)
    estimated_hours_remaining = fields.Float("Estimated Hours Remaining", tracking=True)
    estimated_completion_hours = fields.Float("Estimated Completion Hours", tracking=True)
    quantity_completed = fields.Float("Quantity Completed")
    total_hours_log_internal = fields.Float("Total Hours Logged (Internal)")
    total_hours_log = fields.Float("Total Hours Logged (Public)")
    actual_productivity = fields.Float("Actual Productivity")
    actual_tat = fields.Integer(
        string="Actual TAT (days)",
        compute="_compute_actual_tat",
        store=True,
    )
    week_completed = fields.Char(string="Week Completed", compute="_compute_completion_periods", store=True, )
    month_completed = fields.Char(string="Month Completed", compute="_compute_completion_periods", store=True, )
    poc_ids = fields.Many2many("hr.employee", "project_poc_rel", "project_id", "poc_employee_id", string="In-house POC")
    supervisor_ids = fields.Many2many("hr.employee", "project_supervisor_rel", "project_id", "supervisor_employee_id", string="Supervisor")
    leader_ids = fields.Many2many("hr.employee", "project_leader_rel", "project_id", "leader_employee_id", string="Leader / Right-hand")
    task_count_list = fields.Integer(
        string="Tasks",
        compute="_compute_task_count_list",
        help="Total number of tasks belonging to this project.",
    )

    @api.depends("task_ids")
    def _compute_task_count_list(self):
        """Compute the total number of tasks for the project list view."""
        for project in self:
            project.task_count_list = len(project.task_ids)

    @api.depends("actual_start_date", "actual_completion_date")
    def _compute_actual_tat(self):
        for project in self:
            if project.actual_start_date and project.actual_completion_date:
                delta = project.actual_completion_date - project.actual_start_date
                project.actual_tat = delta.days
            else:
                project.actual_tat = 0

    @api.depends("actual_completion_date")
    def _compute_completion_periods(self):
        """Compute week and month strings based on the actual completion date."""
        for project in self:
            if project.actual_completion_date:
                date_val = project.actual_completion_date
                iso_week = date_val.isocalendar()[1]
                project.week_completed = f"Week {iso_week}"
                project.month_completed = date_val.strftime("%B %Y")
            else:
                project.week_completed = False
                project.month_completed = False

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

    @api.onchange("cluster_id")
    def onchange_cluster_id(self):
        if self.cluster_id:
            self.group_id = False

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
