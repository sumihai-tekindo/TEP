# -*- coding: utf-8 -*-
from odoo import http

# class StiCompany(http.Controller):
#     @http.route('/sti_company/sti_company/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sti_company/sti_company/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sti_company.listing', {
#             'root': '/sti_company/sti_company',
#             'objects': http.request.env['sti_company.sti_company'].search([]),
#         })

#     @http.route('/sti_company/sti_company/objects/<model("sti_company.sti_company"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sti_company.object', {
#             'object': obj
#         })