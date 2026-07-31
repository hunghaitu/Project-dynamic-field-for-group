from odoo import models, fields, api
from odoo.exceptions import ValidationError
from lxml import etree


class DynamicTimesheetLayoutConfig(models.Model):
    _name = "dynamic.timesheet.layout.config"
    _description = "Dynamic Timesheet Layout Configuration"

    name = fields.Char(string="Configuration Name", required=True)
    cluster_id = fields.Many2one("hr.cluster", string="Cluster", required=True)
    group_id = fields.Many2one(
        "hr.group",
        string="Group",
        required=False,
        domain="[('cluster_id', '=', cluster_id)]"
    )

    note = fields.Text(string="Description / Note")
    line_ids = fields.One2many(
        "dynamic.timesheet.layout.config.line",
        "config_id",
        string="Field Configuration"
    )

    _unique_group_config = models.Constraint(
        "UNIQUE(group_id)",
        "Each group can only have one timesheet layout configuration!"
    )

    @api.onchange('group_id', 'cluster_id')
    def _onchange_group_cluster(self):
        if self.cluster_id and self.group_id:
            cluster_template = self.search([
                ('cluster_id', '=', self.cluster_id.id),
                ('group_id', '=', False)
            ], limit=1)
            if cluster_template:
                existing_field_ids = {line.field_id.id for line in self.line_ids if line.field_id}
                new_lines = []
                for line in cluster_template.line_ids:
                    if line.field_id.id not in existing_field_ids:
                        new_lines.append((0, 0, {
                            'field_id': line.field_id.id,
                            'sequence': line.sequence,
                            'line_note': line.line_note,
                        }))
                if new_lines:
                    self.line_ids = [(4, line.id) for line in self.line_ids] + new_lines

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
        config = self.sudo().search([("group_id", "=", group.id)], limit=1)
        data_root = etree.Element("data")
        if config and config.line_ids:
            xpath_insert_page = etree.SubElement(data_root, "xpath", {
                "expr": "//page[@name='settings']",
                "position": "before"
            })
            page_node = etree.SubElement(xpath_insert_page, "page", {
                "string": "Timesheets",
                "name": f"timesheets_page_group_{group.id}",
                "invisible": f"group_id != {group.id}"
            })
            field_timesheet_node = etree.SubElement(page_node, "field", {
                "name": "timesheet_ids",

                "context": "{'default_project_id': id, 'active_id': id}"
            })
            list_node = etree.SubElement(field_timesheet_node, "list", {
                "editable": "bottom"
            })
            for line in config.line_ids.sorted(key=lambda rec: (rec.sequence, rec.id)):
                if line.technical_name:
                    field_attrib = {"name": line.technical_name}
                    if line.is_required:
                        field_attrib["required"] = "1"
                    if line.is_readonly:
                        field_attrib["readonly"] = "1"

                    etree.SubElement(list_node, "field", field_attrib)

        arch_xml = etree.tostring(data_root, encoding="utf-8", pretty_print=True).decode()
        xml_id = f"project_custom.dynamic_timesheet_view_project_group_{group.id}"
        view_domain = [("model", "=", "project.project"), ("key", "=", xml_id)]
        custom_view = self.env["ir.ui.view"].sudo().search(view_domain, limit=1)
        parent_view = self.env.ref("project_custom.view_project_project_form_inherited", raise_if_not_found=False)

        if not parent_view:
            return

        view_vals = {
            "name": f"Timesheet Dynamic View for Group: {group.name}",
            "model": "project.project",
            "inherit_id": parent_view.id,
            "priority": 1300,
            "arch_base": arch_xml,
            "active": True,
        }

        if custom_view:
            custom_view.write({"arch_base": arch_xml})
        else:
            if config and config.line_ids:
                view_vals.update({
                    "key": xml_id,
                    "type": "form",
                })
                self.env["ir.ui.view"].sudo().create(view_vals)

        self.env.registry.clear_cache()


class DynamicTimesheetLayoutConfigLine(models.Model):
    _name = "dynamic.timesheet.layout.config.line"
    _description = "Dynamic Timesheet Layout Configuration Line"
    _order = "sequence, id"

    config_id = fields.Many2one("dynamic.timesheet.layout.config", string="Configuration Ref", ondelete="cascade")
    field_id = fields.Many2one(
        "ir.model.fields",
        string="Field",
        domain="[('model', '=', 'account.analytic.line')]",
        required=True, ondelete="cascade"
    )

    technical_name = fields.Char(related="field_id.name", string="Technical Name", readonly=True)
    field_type = fields.Selection(related="field_id.ttype", string="Type", readonly=True)
    sequence = fields.Integer(string="Sequence", default=10)
    is_required = fields.Boolean(string="Required", default=False)
    is_readonly = fields.Boolean(string="Readonly", default=False)
    line_note = fields.Char(string="Note")

    @api.constrains('field_id', 'config_id')
    def _check_unique_field_per_layout_config(self):
        for record in self:
            duplicates = self.search_count([
                ('config_id', '=', record.config_id.id),
                ('field_id', '=', record.field_id.id),
                ('id', '!=', record.id)
            ])
            if duplicates > 0:
                raise ValidationError(f"The field '{record.field_id.field_description}' has already been added to this layout configuration.")

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        groups = records.mapped("config_id.group_id")
        self.env["dynamic.timesheet.layout.config"]._update_group_views(groups)
        return records

    def write(self, vals):
        groups_before = self.mapped("config_id.group_id")
        res = super().write(vals)
        groups_after = self.mapped("config_id.group_id")
        groups = groups_before | groups_after
        self.env["dynamic.timesheet.layout.config"]._update_group_views(groups)
        return res

    def unlink(self):
        groups = self.mapped("config_id.group_id")
        res = super().unlink()
        self.env["dynamic.timesheet.layout.config"]._update_group_views(groups)
        return res
