from odoo import models, fields, api
from lxml import etree


class ProjectProject(models.Model):
    _inherit = "project.project"

    timesheet_optional_fields = fields.Json(string="Timesheet Optional Fields", default=[])
    group_id = fields.Many2one("hr.group", string="Group")

    @api.model_create_multi
    def create(self, vals_list):
        projects = super().create(vals_list)
        for project in projects:
            if project.group_id:
                self._check_and_generate_group_view(project.group_id)
        return projects

    def write(self, vals):
        res = super().write(vals)
        if "group_id" in vals:
            for project in self:
                if project.group_id:
                    self._check_and_generate_group_view(project.group_id)
        return res

    def _check_and_generate_group_view(self, group):
        configs = self.env["timesheet.field.dynamic.config"].sudo().search([("group_id", "in", group.id)])

        data_root = etree.Element("data")

        xpath_node = etree.SubElement(data_root, "xpath", {"expr": "//page[@name='timesheets_custom_page']//field[@name='timesheet_ids']/list", "position": "inside"})

        for config in configs:
            field_name = config.field_id.name
            etree.SubElement(
                xpath_node,
                "field",
                {
                    "name": field_name,
                    "optional": "hide",

                },
            )

        arch_xml = etree.tostring(data_root, encoding="utf-8", pretty_print=True).decode()

        xml_id = f"project_custom.studio_style_project_project_group_{group.id}"
        view_domain = [("model", "=", "project.project"), ("key", "=", xml_id)]
        custom_view = self.env["ir.ui.view"].sudo().search(view_domain, limit=1)

        parent_view = self.env.ref("project_custom.view_project_project_form_inherited", raise_if_not_found=False)
        if not parent_view:
            return

        view_vals = {
            "name": f"Timesheet Custom View for Group: {group.name}",
            "model": "project.project",
            "inherit_id": parent_view.id,
            "priority": 1200,
            "arch_base": arch_xml,
            "active": True,
        }

        if custom_view:
            custom_view.write({"arch_base": arch_xml})
        else:
            view_vals.update(
                {
                    "key": xml_id,
                    "type": "form",
                }
            )
            self.env["ir.ui.view"].sudo().create(view_vals)

        self.env.registry.clear_cache()

    def action_open_select_fields_wizard(self):
        self.ensure_one()
        group_id = self.env.context.get('temp_group_id') or self.group_id.id
        configs = self.env["timesheet.field.dynamic.config"].sudo().search([("group_id", "in", group_id)])
        currently_selected = self.timesheet_optional_fields or []
        wizard_lines = []
        for config in configs:
            f = config.field_id
            wizard_lines.append((0, 0, {"field_name": f.name, "field_description": f.field_description or f.string, "is_selected": f.name in currently_selected}))

        wizard = self.env["project.project.fields.wizard"].create({"project_id": self.id, "line_ids": wizard_lines, "group_id": group_id})

        view_id = self.env.ref("project_custom.view_project_project_fields_wizard_form").id
        search_view_id = self.env.ref("project_custom.view_project_project_fields_wizard_line_search").id
        return {
            "name": "Select Visible Fields",
            "type": "ir.actions.act_window",
            "res_model": "project.project.fields.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "views": [(view_id, "form")],
            "search_view_id": [search_view_id, "search"],
            "target": "new",
            'context': {
                'default_project_id': self.id,
                'default_group_id': group_id,
            }
        }
