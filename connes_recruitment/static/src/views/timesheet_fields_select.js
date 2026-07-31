/** @odoo-module */

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { onMounted, onWillStart, onWillUpdateProps } from "@odoo/owl";
import { ListRenderer } from "@web/views/list/list_renderer";
import { X2ManyField, x2ManyField } from "@web/views/fields/x2many/x2many_field";

export class TimesheetLinesListRenderer extends ListRenderer {
    static template = "connes_recruitment.TimesheetLinesListRenderer";

    setup() {

        super.setup();

        this.orm = useService("orm");
        this.actionService = useService("action");
        this.projectOptionalFields = [];
        this.currentProjectId = null;

        onWillStart(async () => {
            await this.loadProjectOptionalFields();
        });

        onMounted(() => {
            this._syncOptionalFields();
        });

        onWillUpdateProps(async (nextProps) => {
            const newProjectId = nextProps.list?.context?.default_project_id;
            if (newProjectId !== this.currentProjectId) {
                await this.loadProjectOptionalFields(newProjectId);
            }
        });
    }


    async loadProjectOptionalFields(projectId = null) {
        const targetProjectId = projectId ?? this.props.list?.context?.default_project_id;

        if (!targetProjectId) {
            this.projectOptionalFields = [];
            this.currentProjectId = null;
            this._syncOptionalFields();
            return;
        }

        try {
            const result = await this.orm.call("project.project", "read", [
                [targetProjectId],
                ["timesheet_optional_fields"],
            ]);
            this.projectOptionalFields = result[0]?.timesheet_optional_fields || [];
            this.currentProjectId = targetProjectId;
        } catch (error) {
            console.error("[TimesheetLinesListRenderer] loadProjectOptionalFields error:", error);
            this.projectOptionalFields = [];
        }

        this._syncOptionalFields();
    }


    _syncOptionalFields() {
        if (!this.optionalActiveFields) return;

        const coreFields = new Set(["date", "employee_id", "name", "unit_amount"]);
        const wantVisible = new Set(this.projectOptionalFields);

        for (const fieldName of Object.keys(this.optionalActiveFields)) {
            if (coreFields.has(fieldName)) continue;

            const isVisible = this.optionalActiveFields[fieldName] === true;
            const shouldBeVisible = wantVisible.has(fieldName);

            if (isVisible !== shouldBeVisible) {
                this.toggleOptionalField(fieldName);
            }
        }
    }

    async openSelectFieldsWizard() {
        const context = this.props.list?.context || {};
        const rootRecord = this.props.list?.model?.root;
        const projectId = context.default_project_id || rootRecord?.resId;

        if (!projectId) {
            alert("Please select a Project before configuring visible fields.");
            return;
        }

        let currentGroupId = false;
        const groupData = rootRecord?.data?.group_id;

        if (groupData) {
            // 1. Kiểm tra nếu groupData là một Object/Proxy có chứa thuộc tính id bên trong (Trường hợp của bạn)
            if (typeof groupData === "object" && "id" in groupData) {
                currentGroupId = groupData.id;
            }
            // 2. Trường hợp phòng hờ Odoo trả về mảng [id, name] khi bản ghi đã lưu
            else if (Array.isArray(groupData)) {
                currentGroupId = groupData[0];
            }
            // 3. Trường hợp trả về ID số thuần túy
            else {
                currentGroupId = parseInt(groupData) || false;
            }
        }

        let action;
        try {
            action = await this.orm.call(
                "project.project",
                "action_open_select_fields_wizard",
                [[projectId]],
                {
                    // Đảm bảo ép kiểu context rõ ràng
                    context: Object.assign({}, context, { temp_group_id: currentGroupId })
                }
            );
        } catch (error) {
            console.error("[TimesheetLinesListRenderer] openSelectFieldsWizard error:", error);
            return;
        }

        if (action) {
            this.actionService.doAction(action, {
                onClose: async () => {
                    if (this.props.list?.model?.root) {
                        await this.props.list.model.root.load();
                    }
                    await this.loadProjectOptionalFields(projectId);
                },
            });
        }
    }


    async exportToExcel() {
        const coreFields = new Set(["date", "employee_id", "name", "unit_amount"]);

        const displayedColumns = (this.columns || []).filter((col) => {
            if (coreFields.has(col.name)) return true;
            if (col.optional) {
                return this.optionalActiveFields?.[col.name] === true;
            }
            return col.column_invisible !== true && col.column_invisible !== "True";
        });

        const headers = displayedColumns.map((col) => col.label || col.string || col.name);

        const rows = this.props.list.records.map((record) =>
            displayedColumns.map((column) => {
                const val = this.getFormattedValue(column, record);
                if (val === false || val === null || val === undefined) return "";
                return String(val).replace(/"/g, '""');
            })
        );

        const csvContent = [headers, ...rows]
            .map((row) => row.map((cell) => `"${cell}"`).join(","))
            .join("\n");

        const blob = new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8;" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.setAttribute("href", url);
        link.setAttribute("download", `Timesheets_${new Date().toISOString().split("T")[0]}.csv`);
        link.style.visibility = "hidden";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

export class TimesheetLinesWidget extends X2ManyField {
    static components = {
        ...X2ManyField.components,
        ListRenderer: TimesheetLinesListRenderer,
    };
}

export const timesheetLinesWidget = {
    ...x2ManyField,
    component: TimesheetLinesWidget,
    additionalClasses: ["o_field_many2many"],
};

registry.category("fields").add("timesheet_lines_widget", timesheetLinesWidget);
