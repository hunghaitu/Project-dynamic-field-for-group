# -*- coding: utf-8 -*-
{
    'name': "Connes Recruitment",
    'summary': "Custom recruitment",
    'description': """
    """,
    'author': "Quang",
    'website': "https://www.facebook.com/quang.nguyenhuy.2005",
    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'price': 29.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'depends': ['base', 'mail', 'mail_bot', 'hr', 'hr_recruitment', 'web', 'website', 'hr_timesheet', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'data/menu_data.xml',
        'views/cennos_portal_recruitment.xml',
        'views/connes_recruitment_views.xml',
        'views/cennos_cluster.xml',
        'views/cennos_group.xml',
        'views/project_project.xml',
        'views/project_task_views.xml',
        'views/dynamic_timesheet_layout_config.xml',
        'views/project_task_category.xml',
        'views/project_unit.xml',
        'views/productivity_unit.xml',
        'views/rework_reason.xml',
        'views/overtime_category.xml',
        'views/flex_reason.xml',
        'views/task_output_submission.xml',
        'views/project_task_rework.xml',
    ],
    'images': [
            'static/description/screenshot.png',
        ],
    'assets': {
        'web.assets_backend': [

        ],
    }
}
