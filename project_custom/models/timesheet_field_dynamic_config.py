from odoo import models, fields, api
from lxml import etree
from odoo.exceptions import ValidationError


class TimesheetFieldDepartment(models.Model):
    _name = "timesheet.field.dynamic.config"
    _description = "Timesheet Fields Configuration"

    field_id = fields.Many2one("ir.model.fields", string="Field", domain="[('model', '=', 'account.analytic.line'), ('state', '=', 'manual')]", required=True, ondelete="cascade")
    group_id = fields.Many2one(
        "hr.group",
        string="Group",
        required=False, ondelete="cascade"
    )

    @api.constrains("field_id", "group_id")
    def _check_unique_field_config(self):
        for record in self:
            duplicate_count = self.search_count([
                ("field_id", "=", record.field_id.id), ("group_id", "=", record.group_id.id),
                ("id", "!=", record.id)
            ])
            if duplicate_count > 0:
                raise ValidationError(
                    f"The technical field '{record.field_id.name}' has already been configured! "
                    f"Each field can only be allocated once across the system."
                )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        groups = records.mapped("group_id")
        self._update_group_views(groups)
        return records

    def write(self, vals):
        groups_before = self.mapped("group_id")
        res = super().write(vals)
        groups_after = self.mapped("group_id")

        groups = groups_before | groups_after
        self._update_group_views(groups)
        return res

    def unlink(self):
        groups = self.mapped("group_id")
        res = super().unlink()
        self._update_group_views(groups)
        return res

    @api.model
    def _update_group_views(self, groups):
        if not groups:
            return

        for group in groups:
            self._check_and_generate_group_view(group)

    @api.model
    def _check_and_generate_group_view(self, group):
        if not group:
            return

        configs = self.env["timesheet.field.dynamic.config"].sudo().search([("group_id", "in", group.id)])
        data_root = etree.Element("data")
        if configs:
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
            if configs:
                view_vals.update(
                    {
                        "key": xml_id,
                        "type": "form",
                    }
                )
                self.env["ir.ui.view"].sudo().create(view_vals)

        self.env.registry.clear_cache()
