from odoo import fields, api, models, http, tools, _
from odoo.http import request, Response
from datetime import timedelta, date, datetime
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager, get_records_pager
import calendar, json
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF



class ExpenseSummary(http.Controller):
    
    @http.route('/expense_form', type='http', method="GET", auth='user', website=True, csrf=False)
    def render_expense_form(self, **kwargs):
        """
        Render Add Expense Form Template
        """
        categories = request.env['expense.category'].search([])
        accounts = request.env['bank.account'].search([])
        return request.render('budget_expense_management.expense_form_template',{'categories': categories,
                                                                             'accounts':accounts})
     
     
    @http.route('/my_expenses', type='json', auth="user", 
                website=True, methods=['DELETE'],  csrf=False) 
    def delete_expense(self, **kwargs):
        """
        Delete expense pointed by expense_id
        """
        data = json.loads(request.httprequest.data.decode('utf-8'))

               
        if 'expense_id' in data:
            expense_summary = request.env['expense.summary'] 
            record_to_delete = expense_summary.browse(data['expense_id']).unlink()

        return Response("success", status=200)
    
    
    @http.route('/my_expenses', type='json', auth="user", 
                website=True, methods=['PATCH'],  csrf=False) 
    def update_expense(self, **kwargs):
        """
        Delete expense pointed by expense_id
        """
        try:
            data = json.loads(request.httprequest.data.decode('utf-8'))
            exp_id = request.env['expense.summary'].browse([int(data['exp_id'])])
            if exp_id:
                if data['date']:
                    date_obj = datetime.strptime(data['date'],'%Y-%m-%d').date()
                    exp_id.date = date_obj.strftime(DF)
                if data['category']:
                    catg_obj = request.env['expense.category'].search([('name','=', data['category'])])
                    if catg_obj and catg_obj.name :
                        exp_id.exp_category_id = catg_obj.id
                if data['description']:
                    exp_id.name = data['description']
                if data['account']:
                    account_obj = request.env['bank.account'].search([('name','=', data['account'])])
                    if account_obj and account_obj.name :
                        exp_id.account_journal_id = account_obj.id
                if data['location']:
                    exp_id.location = data['location']
                if data['amount']:
                    exp_id.amount = float(data['amount'].replace(',',''))
        except Exception as exc:
            print(exc)
            #data = {'result': 'failure'}
            #return Response(json.dumps({"no":"i am json"}),content_type='application/json;charset=utf-8',status=410)
            Response.status = "400"
            return "Error"
                    
        #return Response(json.dumps({"yes":"i am json"}),content_type='application/json;charset=utf-8',status=200)
        Response.status = "200"
        return "success"
        
    @http.route('/my_expenses', type='http', auth="user", 
                website=True, methods=['POST'],  csrf=False)
    def add_expense(self, **post):
        """
        Add new expense
        """
        expense_summary = request.env['expense.summary']
        expense_id = expense_summary.create({
                    'name':post.get('name', False),
                    'date':post.get('date', False),
                    'exp_category_id':post.get('category', False),
                    'account_journal_id':post.get('account', False),
                    'amount':post.get('expense_amount', False),
                    'location':post.get('location', False),
                    'user_id': request.env.user.id or False
        })
        return Response("success", status=200)
    
    @http.route('/my_expenses', type='http', auth="user", 
                website=True, methods=['GET'],  csrf=False)
    def show_expense(self, **post):
        """
        Return all expenses
        """
        expense_summary = request.env['expense.summary']
        domain = [('user_id','=', request.env.user.id),('date','<=',fields.Date.today())]
        expenses = expense_summary.search(domain)
        exp_catg_ids = request.env['expense.category'].search([]).mapped('name')
        account_id_list = request.env['bank.account'].search([]).mapped('name')
        values = { 
                    'my_expenses': expenses.sudo(), 
                    'catg_ids' : exp_catg_ids,
                    'accounts' :account_id_list
                 }
        return request.render("budget_expense_management.portal_my_expenses", values)
    
    
    
