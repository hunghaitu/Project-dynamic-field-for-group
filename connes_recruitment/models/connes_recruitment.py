from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from markupsafe import Markup


class ConnesRecruitment(models.Model):
    _name = "connes.recruitment"
    _description = "Cennos - Headcount Change Form"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"

    name = fields.Char(string="Request Title", required=True, tracking=True)
    requested_by = fields.Many2one("res.users", string="Requested by", required=True, default=lambda self: self.env.user)
    recipients = fields.Many2many(
        "res.partner", domain=[("is_company", "=", False)], string="Notification Recipients", help="Partners to notify about this request.", tracking=True
    )
    project_owner = fields.Many2one("res.partner", string="Project Owned By", required=True, domain=[("is_company", "=", True)], tracking=True)
    type_of_request = fields.Selection(
        [
            ("increase", "Headcount Increase"),
            ("decrease", "Headcount Decrease"),
            ("start_lob", "Start a Line of Business (LoB)"),
            ("end_lob", "End a Line of Business (LoB)"),
        ],
        string="Type of Request",
        required=True,
        tracking=True,
    )
    existing_process = fields.Many2one("hr.job", string="Existing Process")
    new_process_name = fields.Char(string="New Process Name")
    current_headcount = fields.Integer(string="Current Headcount")
    headcount_change = fields.Integer(string="Headcount Change (+/-)")
    total_desired_headcount = fields.Integer(string="Total Desired Headcount")
    effective_date = fields.Date(string="Desired Effective Date", tracking=True, default=fields.Date.context_today)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("manager_approve", "Receiving & Processing"),
            ("customer_review", "Customer Review"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        string="Status",
        default="draft",
        tracking=True,
    )
    description = fields.Text(string="Description", tracking=True)

    @api.onchange("current_headcount", "headcount_change")
    def _compute_total_headcount(self):
        for rec in self:
            rec.total_desired_headcount = (rec.current_headcount or 0) + (rec.headcount_change or 0)

    @api.onchange("type_of_request")
    def _onchange_type_of_request(self):
        for rec in self:
            rec.existing_process = rec.new_process_name = False
            if rec.type_of_request == "start_lob":
                rec.headcount_change = 0
                rec.current_headcount = 0
                rec.total_desired_headcount = 0

    def action_approve(self):
        odoobot = self.env.ref("base.partner_root")
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")

        for rec in self:
            if rec.state == "manager_approve":
                rec.state = "customer_review"
                rec.message_post(body=_("Manager approved the headcount change.."))

                for partner in rec.recipients:
                    self._send_odoo_bot_message(partner, rec, odoobot)

                    if partner.email:
                        record_link = f"<a href='{base_url}/web#id={rec.id}&model=connes.recruitment&view_type=form'>{rec.name}</a>"
                        email_body = _("The request <b>%s</b>, created by <b>%s</b>, has been approved by the Manager.<br/>Please review and approve it here: %s") % (
                            rec.name,
                            rec.requested_by.name,
                            record_link,
                        )
                        self._send_notification_email(partner, "Headcount Change - Manager Approved", email_body)

            elif rec.state == "customer_review":
                rec.state = "approved"
                rec.process_job_position()
                rec.message_post(body=_("Customer approved the headcount change."))
                partner = rec.requested_by.partner_id
                self._send_odoo_bot_message(partner, rec, odoobot)

                if partner.email:
                    record_link = f"<a href='{base_url}/web#id={rec.id}&model=connes.recruitment&view_type=form'>{rec.name}</a>"
                    email_body = _("The request <b>%s</b> has been approved by the customer.<br/>View it here: %s") % (rec.name, record_link)
                    self._send_notification_email(partner, "Headcount Change Approved", email_body)

    def _send_odoo_bot_message(self, partner, rec, _odoobot):
        if not partner or not rec or not partner.exists():
            return

        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        record_url = f"{base_url}/web#id={rec.id}&model=connes.recruitment&view_type=form"

        odoobot_user = self.env.ref("base.user_root", raise_if_not_found=False)
        odoobot_partner = odoobot_user.partner_id if odoobot_user else None

        if not odoobot_partner or odoobot_partner == partner:
            return

        Channel = self.env["discuss.channel"].with_user(odoobot_user)

        channel_info = Channel.channel_get([odoobot_partner.id, partner.id])
        channel = Channel.browse(channel_info["id"])

        message = Markup("%s<br/>%s<br/><b><a href='%s'>%s</a></b> <span class=\"o_odoobot_command\">:)</span>") % (
            _("Hello!"),
            _("OdooBot notification: a Headcount Change request has been updated."),
            record_url,
            _(f"{rec.name} (State: {rec.state})"),
        )

        channel.message_post(
            author_id=odoobot_partner.id,
            body=message,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            silent=True,
        )

    def _send_notification_email(self, partner, subject, body):
        mail_values = {
            "subject": subject,
            "body_html": body,
            "email_to": partner.email,
        }
        self.env["mail.mail"].sudo().create(mail_values).send()

    def process_job_position(self):
        Candidate = self.env["hr.candidate"]
        Applicant = self.env["hr.applicant"]
        Stage = self.env["hr.recruitment.stage"]

        for rec in self:
            partner = rec.requested_by.partner_id
            if not partner:
                partner = self.env["res.partner"].create(
                    {
                        "name": rec.requested_by.name,
                        "email": rec.requested_by.email or "",
                        "company_type": "person",
                    }
                )

            candidate = Candidate.search([("partner_id", "=", partner.id)], limit=1)
            if not candidate:
                candidate = Candidate.create({"partner_id": partner.id})
            stage_id = Stage.search([], limit=1).id

            if rec.type_of_request == "increase":
                job = rec.existing_process
                if job:
                    job.no_of_recruitment += rec.current_headcount
                    Applicant.create(
                        {
                            "candidate_id": candidate.id,
                            "partner_name": rec.name,
                            "job_id": job.id,
                            "stage_id": stage_id,
                            "user_id": rec.requested_by.id,
                        }
                    )

            elif rec.type_of_request == "start_lob":
                if not rec.project_owner or not rec.project_owner.exists():
                    raise ValidationError(f"Không tìm thấy thông tin công ty {rec.project_owne.name}.")

                job = self.env["hr.job"].create(
                    {
                        "name": rec.new_process_name,
                        "company_id": rec.project_owner.id,
                        "user_id": rec.requested_by.id,
                        "no_of_recruitment": rec.current_headcount,
                    }
                )
                Applicant.create(
                    {
                        "candidate_id": candidate.id,
                        "partner_name": rec.name,
                        "job_id": job.id,
                        "stage_id": stage_id,
                        "user_id": rec.requested_by.id,
                    }
                )

    def action_send(self):
        for rec in self:
            rec.state = "manager_approve"
            rec.message_post(body=_("The request has been sent for approval."))

    def action_reject(self):
        for rec in self:
            rec.state = "rejected"
            rec.message_post(body=_("The request was rejected."))

    def action_reset_draft(self):
        for rec in self:
            rec.state = "draft"
