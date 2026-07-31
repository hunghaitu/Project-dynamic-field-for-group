from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = "project.task"

    department_id = fields.Many2one("hr.department", "Department")
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

    task_start_date = fields.Datetime("Task Start Date")
    project_unit = fields.Many2one("project.unit", string="Project Unit")
    task_category_id = fields.Many2one("project.task.category", string="Task Category")
    assigned_date = fields.Datetime("Assigned Date")
    task_completion_date = fields.Datetime("Task Completion Date")
    lastest_submission_no = fields.Integer("Latest Submission No.")
    latest_submission_status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("reviewed", "Reviewed"),
        ],
        string="Latest Submission Status",
        help="Status of the latest submission.",
    )

    latest_qa_result = fields.Selection(
        selection=[
            ("approved", "Approved"),
            ("rework_required", "Rework Required"),
            ("rejected", "Rejected"),
        ],
        string="Latest QA Result",
        help="QA decision result for the latest submission. Left empty if not yet reviewed.",
    )

    latest_submitted_by_id = fields.Many2one(
        "hr.employee",
        string="Latest Submitted By",
        help="Employee who clicked submit for QA review on the latest submission.",
    )

    latest_submitted_date = fields.Datetime(
        string="Latest Submitted Date",
        help="Timestamp when the user submitted for QA review.",
    )

    latest_reviewed_date = fields.Datetime(
        string="Latest Reviewed Date",
        help="Timestamp when the QA/TL reviewed the submission.",
    )

    latest_reviewed_by_id = fields.Many2one(
        "hr.employee",
        string="Latest Reviewed By",
        help="QA/TL employee who executed Approve, Request Rework, or Reject action.",
    )

    latest_qa_note = fields.Text(
        string="Latest QA Note",
        help="Notes or feedback provided during the latest QA review.",
    )
    submission_ids = fields.One2many(
        "task.output.submission",
        "task_id",
        string="Output Submissions"
    )
    quantity_completed = fields.Float("Qty Completed")
    total_hours_log_internal = fields.Float("Total Hours Logged (Internal)")
    total_hours_log = fields.Float("Total Hours Logged (Public)")
    productivity_goal = fields.Float("Productivity Goal", tracking=True)
    productivity_unit_id = fields.Many2one("productivity.unit", string="Productivity Unit", tracking=True)
    estimated_productivity = fields.Float("Estimated Productivity", tracking=True)
    estimated_hours_remaining = fields.Float("Estimated Hours Remaining", tracking=True)
    estimated_completion_hours = fields.Float("Estimated Completion Hours", tracking=True)
    actual_productivity = fields.Float("Actual Productivity")
    actual_tat = fields.Integer(
        string="Actual TAT (days)",
        compute="_compute_actual_tat",
        store=True,
    )
    week_completed = fields.Char(string="Week Completed", compute="_compute_completion_periods", store=True, )
    month_completed = fields.Char(string="Month Completed", compute="_compute_completion_periods", store=True, )
    rework_ids = fields.One2many(
        "project.task.rework",
        "task_id",
        string="Rework History",
    )

    @api.onchange("project_id")
    def onchange_project_id(self):
        if self.project_id:
            self.project_unit = self.project_id.project_unit
            self.productivity_unit_id = self.project_id.productivity_unit_id

    @api.depends("task_start_date", "task_completion_date")
    def _compute_actual_tat(self):
        for project in self:
            if project.task_start_date and project.task_completion_date:
                delta = project.task_completion_date - project.task_start_date
                project.actual_tat = delta.days
            else:
                project.actual_tat = 0

    @api.depends("task_completion_date")
    def _compute_completion_periods(self):
        """Compute week and month strings based on the actual completion date."""
        for project in self:
            if project.task_completion_date:
                date_val = project.task_completion_date
                iso_week = date_val.isocalendar()[1]
                project.week_completed = f"Week {iso_week}"
                project.month_completed = date_val.strftime("%B %Y")
            else:
                project.week_completed = False
                project.month_completed = False
