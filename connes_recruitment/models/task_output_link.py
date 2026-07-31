from odoo import fields, models


class TaskOutputLink(models.Model):
    _name = "task.output.link"
    _description = "Task Output Submission Link"
    _order = "id"

    submission_id = fields.Many2one(
        "task.output.submission",
        string="Submission",
        required=True,
        ondelete="cascade",
        help="Parent submission for this output link."
    )

    name = fields.Char(
        string="Link Name",
        required=True,
        help="Name or title describing the output link."
    )

    url = fields.Char(
        string="URL",
        required=True,
        help="Web link/address to the output deliverable."
    )

    note = fields.Char(
        string="Note",
        help="Additional remarks or notes regarding this link."
    )
