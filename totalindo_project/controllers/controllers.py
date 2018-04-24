# -*- coding: utf-8 -*-
from odoo import http

# class TepProject(http.Controller):
#     @http.route('/tep_project/tep_project/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/tep_project/tep_project/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('tep_project.listing', {
#             'root': '/tep_project/tep_project',
#             'objects': http.request.env['tep_project.tep_project'].search([]),
#         })

#     @http.route('/tep_project/tep_project/objects/<model("tep_project.tep_project"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('tep_project.object', {
#             'object': obj
#         })