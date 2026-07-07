# -*- coding: utf-8 -*-
{
    'name': "Project Custom",
    'summary': "Project",
    'description': """
    """,
    'author': "Quang",
    'website': "https://www.facebook.com/quang.nguyenhuy.2005",
    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'price': 29.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'depends': ['base', 'mail', 'mail_bot', 'hr', 'hr_timesheet', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_group.xml',
        # 'views/project_task_views.xml',
        'views/timesheet_field_dynamic_config.xml',
        'views/project_project.xml',
        'wizard/project_project_fields_wizard.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'project_custom/static/src/**/*.js',
            'project_custom/static/src/**/*.xml',
        ],
    },
    'application': True,
    'auto_install': False,
}
