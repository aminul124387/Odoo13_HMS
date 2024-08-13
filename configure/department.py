from odoo import fields, models, api


class DepartmentConfiguration(models.Model):
    _name = 'department.config'
    _rec_name = "dept_name"

    dept_name = fields.Char("Department Name")
    parent_dept = fields.Many2one('department.config', 'Parent Department')

    _sql_constraints = [         # Unique Item field Validation
        ('unique_department_name', 'unique (dept_name)', 'Please Give Unique Department Name')
    ]


