# -*- coding: utf-8 -*-
from odoo import http

# class AccountingTotalindo(http.Controller):
#     @http.route('/accounting_totalindo/accounting_totalindo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/accounting_totalindo/accounting_totalindo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('accounting_totalindo.listing', {
#             'root': '/accounting_totalindo/accounting_totalindo',
#             'objects': http.request.env['accounting_totalindo.accounting_totalindo'].search([]),
#         })

#     @http.route('/accounting_totalindo/accounting_totalindo/objects/<model("accounting_totalindo.accounting_totalindo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('accounting_totalindo.object', {
#             'object': obj
#         })