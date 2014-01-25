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

```python
from django.db import models
from django.core.urlresolvers import reverse
from carteblanche.models import Verb, Noun

class ProjectVerb(Verb):
    display_name = "Human Readable Verb Name"
    def is_available(self, user):
        #insert your own conditional logic here to determine 
        #if this user has permission to do this action
        if self.noun.owners.filter(id=user.id).count() > 0:
            return True
        else:
            return False

    def get_url(self):
        #use django reverse to spit out the url of the action 
        #for the given model
        return reverse(
            viewname='project_action_view_name', 
            args=[self.noun.id], 
            current_app='app_name'
            )

class Project(models.Model, Noun):
    owners = models.ManyToManyField(Person)
    verb_classes = [ProjectVerb]

    def get_verbs(self):
        verbs = [
            ProjectVerbs(self)
        ]
        return actions
```

Use in a view 

```python
    class ProjectsView(TemplateView, Noun):
        template_name = 'list.html'
        verb_classes = [ProjectCreateAction]

        def get_context_data(self, **kwargs):
            context = super(ProjectsView, self).get_context_data(**kwargs)
            context['available_actions'] = self.get_available_verbs(self.request.user)
            return context
```

Use inheretance to avoid running the same 'is_available' method twice.
The availability_key should be the same string for any Verbs that have identical 'is_available' methods.

```python
class ProjectMemberVerb(cb.Verb):
    availability_key = "is_member"
    def is_available(self, user):
        return self.noun.is_member(user)

class ProjectUploadVerb(ProjectMemberVerb):
    display_name = "Upload Media"

    def get_url(self):
        return "projects/upload"

class ProjectPostVerb(ProjectMemberVerb):
    display_name = "Post"

    def get_url(self):
        return "/projects/post"

class Project(cb.Noun):
    run_count = 0
    verb_classes = [ProjectUploadVerb, ProjectPostVerb]

    def is_member(self, user):
        self.run_count += 1
        return True
```

You can override the 'get_verbs'  method if you have custom logic.

```python
class Project(models.Model, Noun):
    owners = models.ManyToManyField(Person)

    def get_verbs(self):
        verbs = [
            ProjectVerbs(self)
        ]
        return verbs
```

Displaying in a Template

```html
<ul>
  {% for verb in available_verbs %}
      <li><a href="{{ verb.url }}">{{ verb.display_name }}</a></li>
  {% endfor %}
</ul>
```

