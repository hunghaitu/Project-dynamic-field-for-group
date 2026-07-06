from odoo import models, fields, api


class ProjectProjectFieldsWizard(models.TransientModel):
    _name = "project.project.fields.wizard"
    _description = "Wizard select field for timesheet"

    project_id = fields.Many2one("project.project", string="Project", required=True, ondelete="cascade")
    group_id = fields.Many2one('hr.group', string="Group")
    line_ids = fields.One2many("project.project.fields.wizard.line", "wizard_id", string="List fields")
    search_text = fields.Char(string="Search Fields")

    filtered_line_ids = fields.One2many(
        "project.project.fields.wizard.line",
        compute="_compute_filtered_line_ids",
        inverse="_inverse_filtered_line_ids",
        string="Visible Fields"
    )

    @api.depends("search_text", "line_ids")
    def _compute_filtered_line_ids(self):
        """ Dynamically filters the visible fields inside the grid based on the search input keyword. """
        for wizard in self:
            if not wizard.search_text:
                wizard.filtered_line_ids = wizard.line_ids
            else:
                search_key = wizard.search_text.strip().lower()
                matched_lines = wizard.line_ids.filtered(
                    lambda line, kw=search_key: (line.field_description and kw in line.field_description.lower()) or
                                                (line.field_name and kw in line.field_name.lower())
                )
                wizard.filtered_line_ids = matched_lines

    def _inverse_filtered_line_ids(self):
        """ Inverse method required to ensure computed One2many lines remain editable on the UI interface. """

    def action_apply(self):
        """ Computes all checked options from the raw data lines and stores them on the linked project record. """
        self.ensure_one()
        selected_fields = self.line_ids.filtered(lambda line: line.is_selected).mapped("field_name")
        new_group_id = self.env.context.get('default_group_id')
        self.project_id.sudo().write({"timesheet_optional_fields": selected_fields, "group_id": new_group_id})
        return {"type": "ir.actions.act_window_close"}


class ProjectProjectFieldsWizardLine(models.TransientModel):
    _name = "project.project.fields.wizard.line"
    _description = "Details"
    _order = "field_name"

    wizard_id = fields.Many2one("project.project.fields.wizard", ondelete="cascade")
    field_name = fields.Char(string="Field Name")
    field_description = fields.Char(string="Field Description")
    is_selected = fields.Boolean(string="Is Selected")
