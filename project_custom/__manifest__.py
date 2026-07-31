# -*- coding: utf-8 -*-
{
    'name': "Dynamic timesheet fields on Project",
    'summary': "Dynamic timesheet fields on Project",
    'description': """Config dynamic timesheet fields on Project for each group
    """,
    'author': "Quang",
    'website': "https://www.facebook.com/quang.nguyenhuy.2005",
    'category': 'Uncategorized',
    'version': '19.0.1.0.0',
    'price': 29.00,
    'currency': 'USD',
    'license': 'OPL-1',
    'depends': ['base', 'hr', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_cluster.xml',
        'views/hr_group.xml',
        'views/project_project.xml',
        'views/dynamic_timesheet_layout_config.xml',

    ],
    'images': [
            'static/description/screenshot.png',
        ],
    'assets': {
        'web.assets_backend': [

        ],
    }
}
