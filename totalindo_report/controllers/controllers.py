# -*- coding: utf-8 -*-
from odoo import http

# class TotalindoReport(http.Controller):
#     @http.route('/totalindo_report/totalindo_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/totalindo_report/totalindo_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('totalindo_report.listing', {
#             'root': '/totalindo_report/totalindo_report',
#             'objects': http.request.env['totalindo_report.totalindo_report'].search([]),
#         })

#     @http.route('/totalindo_report/totalindo_report/objects/<model("totalindo_report.totalindo_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('totalindo_report.object', {
#             'object': obj
#         })