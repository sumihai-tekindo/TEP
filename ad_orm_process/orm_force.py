from odoo import fields,models
from odoo import netsvc
# from openerp.tools.safe_eval import safe_eval as eval

class orm_force(models.Model):
	_name = "orm.force"

	name		= fields.Char("Name",size=128,required=True)
	eval_text	= fields.Text("Eval Text ORM")
	exec_text	= fields.Text("Exec Text ORM")
	result	= fields.Text("Result")

	def execute_orm(self,):
		# if not context:context={}
		wf_service = netsvc.LocalService("workflow")
		for force in self:
			cp=compile(force.eval_text,'<string>', 'exec')
			exec(cp)
			if force.exec_text:
				cp2=compile(force.exec_text,'<string>', 'exec')
				exec(cp2)
				print "result===============",result
			self.write({"result":result})
		return True