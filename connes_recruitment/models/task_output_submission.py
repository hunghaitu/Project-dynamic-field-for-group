from odoo import fields, models, api


class TaskOutputSubmission(models.Model):
    _name = "task.output.submission"
    _description = "Task Output Submission"
    _order = "attempt_no desc, id desc"

    task_id = fields.Many2one(
        "project.task",
        string="Task",
        required=True,
        ondelete="cascade",
        help="Task associated with this output submission."
    )

    attempt_no = fields.Integer(
        string="Attempt No.",
        help="Generated sequence number when Agent clicks Submit for QA review. Left empty/0 on Draft."
    )
    submission_status = fields.Selection(
        selection=[
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("reviewed", "Reviewed"),
        ],
        string="Submission Status",
        default="draft",
        required=True,
        help="Status of the submission displayed using statusbar widget."
    )
    output_link_ids = fields.One2many(
        "task.output.link",
        "submission_id",
        string="Output Links"
    )
    attachment_ids = fields.Many2many(
        "ir.attachment",
        "task_output_submission_attachment_rel",
        "submission_id",
        "attachment_id",
        string="Attachments"
    )
    output_note = fields.Text(string="Output Note")
    submitted_by_id = fields.Many2one(
        "hr.employee",
        string="Submitted By"
    )
    submitted_date = fields.Datetime(string="Submitted Date")
    qa_result = fields.Selection(
        selection=[
            ("approved", "Approved"),
            ("rework_required", "Rework Required"),
            ("rejected", "Rejected"),
        ],
        string="QA Result",
        help="QA decision result displayed using badge widget."
    )
    reviewed_by_id = fields.Many2one(
        "hr.employee",
        string="Reviewed By"
    )
    reviewed_date = fields.Datetime(string="Reviewed Date")
    qa_note = fields.Text(string="QA Note")
    link_count = fields.Integer(
        string="Links",
        compute="_compute_counts",
        help="Total number of output links."
    )
    file_count = fields.Integer(
        string="Files",
        compute="_compute_counts",
        help="Total number of attached files."
    )

    @api.depends("output_link_ids", "attachment_ids")
    def _compute_counts(self):
        for rec in self:
            rec.link_count = len(rec.output_link_ids)
            rec.file_count = len(rec.attachment_ids)

    def action_submit_for_qa(self):
        self.ensure_one()
        self.submission_status = "submitted"
