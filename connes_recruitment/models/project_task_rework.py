from odoo import fields, models


class ProjectTaskRework(models.Model):
    _name = "project.task.rework"
    _description = "Project Task Rework History"
    _order = "rework_no desc, id desc"

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        required=True,
        ondelete="cascade",
        help="Task associated with this rework record.",
    )

    rework_no = fields.Integer(
        string="Rework No.",
        required=True,
        help="Auto-incremented rework sequence number per task.",
    )

    submission_id = fields.Many2one(
        "task.output.submission",
        string="Related Submission",
        required=True,
        ondelete="restrict",
        help="The output submission that triggered this rework request.",
    )

    rework_reason_id = fields.Many2one(
        "rework.reason",
        string="Rework Reason",
        required=True,
        ondelete="restrict",
        help="Predefined reason category for requesting rework.",
    )

    rework_note = fields.Text(
        string="Rework Note",
        required=True,
        help="Detailed explanation or feedback on why rework is needed.",
    )

    requested_by_id = fields.Many2one(
        "hr.employee",
        string="Requested By",
        required=True,
        help="QA or TL employee who requested the rework.",
    )

    requested_date = fields.Datetime(
        string="Requested Date",
        default=fields.Datetime.now,
        required=True,
        help="Timestamp when the rework was requested.",
    )

    resubmitted_date = fields.Datetime(
        string="Resubmitted Date",
        help="Timestamp when the Agent resubmitted the corrected task.",
    )

    status = fields.Selection(
        selection=[
            ("open", "Open"),
            ("resubmitted", "Resubmitted"),
            ("closed", "Closed"),
        ],
        string="Status",
        default="open",
        required=True,
        help="Current state of the rework request.",
    )
