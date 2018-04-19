# -*- coding: utf-8 -*-
from odoo import http

# class PurchaseTotalindo(http.Controller):
#     @http.route('/purchase_totalindo/purchase_totalindo/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_totalindo/purchase_totalindo/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_totalindo.listing', {
#             'root': '/purchase_totalindo/purchase_totalindo',
#             'objects': http.request.env['purchase_totalindo.purchase_totalindo'].search([]),
#         })

#     @http.route('/purchase_totalindo/purchase_totalindo/objects/<model("purchase_totalindo.purchase_totalindo"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_totalindo.object', {
#             'object': obj
#         })