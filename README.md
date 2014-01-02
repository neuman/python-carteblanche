django-menu-actions
===================

Module to hold and serialize the in-memory relationship between urls and objects and users.


Django-money
-----------
Django versions supported: 1.4.x, 1.5.x, 1.6.x

Python versions supported: 2.6.x, 2.7.x, pypy 2.1, 3.2.x*, 3.3.x*


Installation
------------
You can obtain the source code for django-money from here:

    https://github.com/neuman/django-menu-actions

Usage
-----

Use in models

    from menu-actions import MenuAction, Actionable
    from django.core.urlresolvers import reverse

	class ProjectAction(MenuAction):
	    display_name = "Human Readable Action Name"
	    def is_available(self, user):
	    	#insert your own conditional logic here to determine if this user has permission to do this action
	        if self.instance.owners.filter(id=user.id).count() > 0:
	            return True
	        else:
	            return False

	    def get_url(self):
	    	#use django reverse to spit out the url of the action for the given model
	        return reverse(viewname='project_action_view_name', args=[self.instance.id], current_app='app_name')

	class Project(models.Model, Actionable):
	    owners = models.ManyToManyField(Person)

	    def get_actions(self):
	        actions = [
	            ProjectAction(self)
	        ]
	        return actions

Use in a view 

	class ProjectsView(TemplateView, Actionable):
	    template_name = 'list.html'

	    def get_actions(self):
	        return [
	            cm.ProjectCreateAction()
	            ]

	    def get_context_data(self, **kwargs):
	        context = super(ProjectsView, self).get_context_data(**kwargs)
	        context['available_actions'] = self.get_available_actions(self.request.user)
	        return context