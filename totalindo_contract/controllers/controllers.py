# -*- coding: utf-8 -*-
from odoo import http

# class StiContract(http.Controller):
#     @http.route('/sti_contract/sti_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sti_contract/sti_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sti_contract.listing', {
#             'root': '/sti_contract/sti_contract',
#             'objects': http.request.env['sti_contract.sti_contract'].search([]),
#         })

#     @http.route('/sti_contract/sti_contract/objects/<model("sti_contract.sti_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sti_contract.object', {
#             'object': obj
#         })