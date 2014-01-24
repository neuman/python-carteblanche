python-carteblanche
===================

A menuing system with the unlimited power of symantics. Holds and serializes the in-memory relationship between urls and objects and users.


Installation
------------
You can obtain the source code for django-menu-actions from here:

    https://github.com/neuman/django-menu-actions

Usage
-----

Use in models

    from django.db import models
    from django.core.urlresolvers import reverse
    from carteblanche.models import Verb, Noun

	class ProjectVerb(Verb):
	    display_name = "Human Readable Verb Name"
	    def is_available(self, user):
	    	#insert your own conditional logic here to determine 
	    	#if this user has permission to do this action
	        if self.instance.owners.filter(id=user.id).count() > 0:
	            return True
	        else:
	            return False

	    def get_url(self):
	    	#use django reverse to spit out the url of the action 
	    	#for the given model
	        return reverse(
	        	viewname='project_action_view_name', 
	        	args=[self.instance.id], 
	        	current_app='app_name'
	        	)

	class Project(models.Model, Noun):
	    owners = models.ManyToManyField(Person)

	    def get_verbs(self):
	        verbs = [
	            ProjectVerbs(self)
	        ]
	        return actions

Use in a view 

	class ProjectsView(TemplateView, Noun):
	    template_name = 'list.html'

	    def get_verbs(self):
	        return [
	            cm.ProjectCreateAction()
	            ]

	    def get_context_data(self, **kwargs):
	        context = super(ProjectsView, self).get_context_data(**kwargs)
	        context['available_actions'] = self.get_available_verbs(self.request.user)
	        return context

Displaying in a Template

      <ul>
        {% block left_menu %}
          {% for verb in available_verbs %}
          	<li><a href="{{ verb.url }}">{{ verb.display_name }}</a></li>
          {% endfor %}
        {% endblock %}
      </ul>