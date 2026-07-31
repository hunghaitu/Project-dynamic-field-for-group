from odoo import http, _
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager


class ConnesRecruitmentPortal(CustomerPortal):
    def _prepare_portal_layout_values(self):
        values = super()._prepare_portal_layout_values()
        recruitment_count = request.env["connes.recruitment"].sudo().search_count([])
        values.update(
            {
                "recruitment_count": recruitment_count,
            }
        )
        return values

    def _get_my_recruitments_searchbar_sortings(self):
        return {
            "date": {"label": _("Effective Date"), "order": "effective_date desc"},
            "name": {"label": _("Title"), "order": "name asc"},
            "state": {"label": _("Status"), "order": "state asc"},
        }

    def _get_my_recruitments_searchbar_filters(self):
        return {
            "all": {"label": _("All"), "domain": []},
            "draft": {"label": _("Draft"), "domain": [("state", "=", "draft")]},
            "manager_approve": {"label": _("Receiving & Processing"), "domain": [("state", "=", "manager_approve")]},
            "customer_review": {"label": _("Customer Review"), "domain": [("state", "=", "customer_review")]},
            "approved": {"label": _("Approved"), "domain": [("state", "=", "approved")]},
            "rejected": {"label": _("Rejected"), "domain": [("state", "=", "rejected")]},
        }

    @http.route(["/my/recruitments", "/my/recruitments/page/<int:page>"], type="http", auth="user", website=True)
    def portal_my_recruitments(self, page=1, sortby="date", filterby="all", **_kw):
        values = self._prepare_portal_layout_values()
        Recruitments = request.env["connes.recruitment"].sudo()

        searchbar_filters = self._get_my_recruitments_searchbar_filters()
        domain = searchbar_filters[filterby]["domain"] if filterby in searchbar_filters else []

        searchbar_sortings = self._get_my_recruitments_searchbar_sortings()
        sort_order = searchbar_sortings[sortby]["order"] if sortby in searchbar_sortings else "effective_date desc"

        recruitment_count = Recruitments.search_count(domain)
        pager = portal_pager(
            url="/my/recruitments",
            total=recruitment_count,
            page=page,
            step=10,
            url_args={"sortby": sortby, "filterby": filterby},
        )

        recruitments = Recruitments.search(domain, order=sort_order, limit=10, offset=pager["offset"])

        values.update(
            {
                "recruitments": recruitments,
                "page_name": "recruitment",
                "pager": pager,
                "default_url": "/my/recruitments",
                "searchbar_sortings": searchbar_sortings,
                "searchbar_filters": searchbar_filters,
                "sortby": sortby,
                "filterby": filterby,
            }
        )
        return request.render("connes_recruitment.portal_my_recruitments", values)

    @http.route(["/my/recruitment/<int:recruitment_id>"], type="http", auth="user", website=True)
    def portal_my_recruitment_detail(self, recruitment_id=None, **_kw):
        recruitment = request.env["connes.recruitment"].sudo().browse(recruitment_id)
        if not recruitment.exists():
            return request.not_found()

        recipient_names = ", ".join([r.name for r in recruitment.recipients]) if recruitment.recipients else "None"

        values = {
            "page_name": "recruitment_detail",
            "recruitment": recruitment,
            "recipient_names": recipient_names,
        }
        return request.render("connes_recruitment.portal_my_recruitment_detail", values)

    @http.route(["/my/recruitment/create"], type="http", auth="user", website=True, methods=["GET", "POST"])
    def portal_my_recruitment_create(self, **post):
        if request.httprequest.method == "POST":
            effective_date = post.get("effective_date") or False

            recipients = request.httprequest.form.getlist("recipients")
            recipients_ids = [(6, 0, list(map(int, recipients)))] if recipients else False

            vals = {
                "name": post.get("name"),
                "project_owner": int(post.get("project_owner")) if post.get("project_owner") else False,
                "type_of_request": post.get("type_of_request"),
                "current_headcount": int(post.get("current_headcount") or 0),
                "headcount_change": int(post.get("headcount_change") or 0),
                "total_desired_headcount": int(post.get("total_desired_headcount") or 0),
                "effective_date": effective_date,
                "requested_by": request.env.user.id,
                "existing_process": int(post.get("existing_process")) if post.get("existing_process") else False,
                "new_process_name": post.get("new_process_name"),
                "description": post.get("description"),
                "recipients": recipients_ids,
            }

            request.env["connes.recruitment"].sudo().create(vals)
            return request.redirect("/my/recruitments")

        project_owners = request.env["res.partner"].sudo().search([("is_company", "=", True)])
        recipients = request.env["res.partner"].sudo().search([("is_company", "=", False)])
        processes = request.env["hr.job"].sudo().search([])

        return request.render(
            "connes_recruitment.portal_my_recruitment_create",
            {
                "project_owners": project_owners,
                "recipients": recipients,
                "processes": processes,
            },
        )

    @http.route(["/my/recruitment/<int:recruitment_id>/edit"], type="http", auth="user", website=True, methods=["GET", "POST"])
    def portal_my_recruitment_edit(self, recruitment_id, **post):
        recruitment = request.env["connes.recruitment"].sudo().browse(recruitment_id)
        if not recruitment.exists():
            return request.not_found()

        if request.httprequest.method == "POST":
            recipients = request.httprequest.form.getlist("recipients")
            recipients_ids = [(6, 0, list(map(int, recipients)))] if recipients else False

            recruitment.sudo().write(
                {
                    "name": post.get("name"),
                    "project_owner": int(post.get("project_owner")) if post.get("project_owner") else False,
                    "type_of_request": post.get("type_of_request"),
                    "current_headcount": int(post.get("current_headcount") or 0),
                    "headcount_change": int(post.get("headcount_change") or 0),
                    "total_desired_headcount": int(post.get("total_desired_headcount") or 0),
                    "effective_date": post.get("effective_date"),
                    "existing_process": int(post.get("existing_process")) if post.get("existing_process") else False,
                    "new_process_name": post.get("new_process_name"),
                    "description": post.get("description"),
                    "recipients": recipients_ids,
                }
            )
            return request.redirect(f"/my/recruitment/{recruitment.id}")

        project_owners = request.env["res.partner"].sudo().search([("is_company", "=", True)])
        recipients = request.env["res.partner"].sudo().search([("is_company", "=", False)])
        processes = request.env["hr.job"].sudo().search([])

        return request.render(
            "connes_recruitment.portal_my_recruitment_edit",
            {
                "recruitment": recruitment,
                "project_owners": project_owners,
                "recipients": recipients,
                "processes": processes,
            },
        )

    @http.route(["/my/recruitment/<int:recruitment_id>/delete"], type="http", auth="user", website=True)
    def portal_my_recruitment_delete(self, recruitment_id):
        recruitment = request.env["connes.recruitment"].sudo().browse(recruitment_id)
        if recruitment.exists():
            recruitment.unlink()
        return request.redirect("/my/recruitments")

    @http.route(["/my/recruitment/<int:rec_id>/send"], type="http", auth="user", website=True)
    def portal_recruitment_send(self, rec_id, **_kw):
        rec = request.env["connes.recruitment"].sudo().browse(rec_id)

        if not rec.exists():
            return request.not_found()

        if rec.requested_by.id != request.env.user.id:
            return request.redirect("/my/recruitments")

        if rec.state == "draft":
            rec.action_send()

        return request.redirect(f"/my/recruitment/{rec_id}")

    @http.route(["/my/recruitment/<int:rec_id>/reset"], type="http", auth="user", website=True)
    def portal_recruitment_reset(self, rec_id, **_kw):
        rec = request.env["connes.recruitment"].sudo().browse(rec_id)

        if not rec.exists():
            return request.not_found()

        if rec.requested_by.id != request.env.user.id:
            return request.redirect("/my/recruitments")

        if rec.state == "manager_approve":
            rec.action_reset_draft()

        return request.redirect(f"/my/recruitment/{rec_id}")

    @http.route(["/my/recruitment/<int:rec_id>/approve"], type="http", auth="user", website=True)
    def portal_recruitment_approve(self, rec_id, **_kw):
        rec = request.env["connes.recruitment"].sudo().browse(rec_id)

        if not rec.exists():
            return request.not_found()

        if rec.requested_by.id != request.env.user.id:
            return request.redirect("/my/recruitments")

        if rec.state == "customer_review":
            rec.action_approve()

        return request.redirect(f"/my/recruitment/{rec_id}")

    @http.route(["/my/recruitment/<int:rec_id>/reject"], type="http", auth="user", website=True)
    def portal_recruitment_reject(self, rec_id, **_kw):
        rec = request.env["connes.recruitment"].sudo().browse(rec_id)

        if not rec.exists():
            return request.not_found()

        if rec.requested_by.id != request.env.user.id:
            return request.redirect("/my/recruitments")

        if rec.state == "customer_review":
            rec.action_reject()

        return request.redirect(f"/my/recruitment/{rec_id}")
