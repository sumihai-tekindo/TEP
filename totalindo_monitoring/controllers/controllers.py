# -*- coding: utf-8 -*-
from odoo import http

# class TotalindoMonitoring(http.Controller):
#     @http.route('/totalindo_monitoring/totalindo_monitoring/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/totalindo_monitoring/totalindo_monitoring/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('totalindo_monitoring.listing', {
#             'root': '/totalindo_monitoring/totalindo_monitoring',
#             'objects': http.request.env['totalindo_monitoring.totalindo_monitoring'].search([]),
#         })

#     @http.route('/totalindo_monitoring/totalindo_monitoring/objects/<model("totalindo_monitoring.totalindo_monitoring"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('totalindo_monitoring.object', {
#             'object': obj
#         })