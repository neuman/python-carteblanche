WARNING: This readme is out of date in the development branch, please refer to [carteblanche-django-starter](https://www.google.com) for an example project that demonstrates 

python-carteblanche
===================

A menuing system of unlimited power. Holds and serializes the in-memory relationship between urls and objects and users.


Installation
------------
You can obtain the source code for carteblanche from here:

    https://github.com/neuman/python-carteblanche

Or install it with pip from the console

	pip install carteblanche

Add 'carteblanche' to your django settings INSTALLED_APPS array.

Changes
-------
This version contains significant changes from the original version and substantially breaks the API.  The decision to break the original API was not made lightly, but was deemed necesary.  The original version was created to see if there was interest in such a tool and was met with TONS of downloads.  From now on I will attempt to keep the API as in tact as possible.

Fundamentally carteblanche is designed to make the process of developing an MVC app closer to the proccess of designing one.  Designers, product owners and users tend to think of software in terms of:

* What are the objects
* What actions are available on those objects
* Who can perform which actions on which objects at what time

Carteblanche makes it possible to structure your project in a way that directly mirrors that thought process.  By breaking your permissions out into reusable verb classes that include permission conditions, it becomes possible to automatically:

* Dynamically generate navigation appropriate for each user
* Dynamically allow or block each user's access to specific views
* Avoid spaghetti code by consistently handing condition variables down from model to view to template

There are three major components in Carteblanche:

* Verb class
* Noun mixin
* NounView mixin

A verb class glues together a view, its named URL, a particular model, and a function that determines if the view is available to the requesting user.

The Noun mixin is intended to be mixed into a model class and along with the attribute 'verb_classes' makes the model aware of what verbs to check availability for.

The NounView mixin is intended to be mixed in with a View class and allows the view to be aware of what noun it represents.


The Verbs File
--------------

Your first step is to create a verbs.py file. This is typically done at the same level as your models.py file.  This file will contain the conditional permissions for your entire app in once centralized location which makes for very easy adjustments later on when your designer/product owner/user decides they want a change.

Start out by importing the carteblanche basics, and putting together a class that includes some simple info for convenience.  The 'condition_name' attribute exists to avoid repeatedly running the same 'is_available' function.  If a Verb has a 'condition_name', Carteblanche stores the result of its 'is_available' function temporarily and skips running 'is_available' for any following Verbs with the same 'condition_name' on the Noun being checked.  This sounds super complicated, but in practice is achieved by simple inheritance. 

```python
from django.core.urlresolvers import reverse
from carteblanche.base import Noun
from carteblanche.mixins import DjangoVerb, availability_login_required

APPNAME = 'core'

class CoreVerb(DjangoVerb):
    app = APPNAME
    condition_name = 'is_public'
```

Next, add base classes for simple 'is_authenticated' and 'is_not_authenticated' conditions.  These may become a part of the next release, but because avoiding colisions in condition names are so critical, it's left up to you to explicitly write your own for now. Inherit from these for any Verbs that should only be available to users who are either logged in or not such as 'SiteJoinVerb' and 'SiteLoginVerb' below.

```python
class AuthenticatedVerb(CoreVerb):
    '''
    abstract class for all verbs only visible to authenticated users
    '''
    condition_name = 'is_authenticated'
    required = True

    def is_available(self, user):
        return user.is_authenticated()


class NotAuthenticatedVerb(CoreVerb):
    '''
    abstract class for all verbs only visible to users who are not authenticated
    '''
    condition_name = 'is_not_authenticated'
    required = True

    def is_available(self, user):
        #only available to non-logged in users
        if user.is_authenticated():
            return False
        return True

class SiteJoinVerb(NotAuthenticatedVerb):
    display_name = "Join Indiepen"
    view_name='user_create'


class SiteLoginVerb(NotAuthenticatedVerb):
    display_name = "Login"
    view_name='user_login'
```

Lets assume that our app has a model called 'Sprocket' that has a ManyToMany of it's members.  Our urls.py file has named urls for:

* 'sprocket_detail' which should be available to anyone logged in
* 'sprocket_update' which should be available only to users listed in the Sprocket's members
* 'sprocket_delete' which should be available only to users listed in the Sprocket's members

We would add the following to our verbs.py file

```python
class SprocketDetailVerb(AuthenticatedVerb):
    display_name = "View Sprocket"
    view_name = 'sprocket_detail'

    def get_url(self):
        return reverse(viewname=self.view_name, args=[self.noun.id], current_app=self.app)

class SprocketeerVerb(CoreVerb):
    '''
    abstract class for all verbs available only to a sprocket's sprocketeers
    '''
    denied_message = "You must be one of the sprocket's sprocketeers to upload to this post."
    condition_name = "is_sprocketeer"

    @availability_login_required
    def is_available(self, user):
        return self.noun.is_sprocketeer(user)

    def get_url(self):
        return reverse(viewname=self.view_name, args=[self.noun.id], current_app=self.app)


class SprocketUpdateVerb(SprocketeerVerb):
    display_name = "Update Sprocket"
    view_name = 'sprocket_update'


class SprocketDeleteVerb(SprocketeerVerb):
    display_name = "Delete Sprocket"
    view_name = 'sprocket_delete'
```


Usage
-----

###Use in a model

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
        #I use django reverse to spit out the url of the action 
        #for the given model but you can substitute your own logic
        return reverse(
            viewname='project_action_view_name', 
            args=[self.noun.id], 
            current_app='app_name'
            )

class Project(models.Model, Noun):
    owners = models.ManyToManyField(Person)
    verb_classes = [ProjectVerb]

```

###Use in a view 

```python
    class ProjectsView(TemplateView, Noun):
        template_name = 'whatever.html'
        verb_classes = [ProjectCreateAction]

        def get_context_data(self, **kwargs):
            context = super(ProjectsView, self).get_context_data(**kwargs)
            context['available_actions'] = self.get_available_verbs(self.request.user)
            return context
```

###Use inheretance to avoid running the same query twice

If some of your verbs need to run the same query to check availability, you can specify an `avalability_key` and `get_available_verbs` will store the value returned from that verb's `is_available` method.  Any verbs that are checked after that with the same `availability_key` will use the stored value.  Inheretance is a simple way to do this without rewriting the `avalability_key` or shared `is_available` method.

```python
class ProjectMemberVerb(Verb):
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

class Project(Noun):
    run_count = 0
    verb_classes = [ProjectUploadVerb, ProjectPostVerb]

    def is_member(self, user):
        self.run_count += 1
        return True
```

###You can override the 'get_verbs'  method if you have custom logic.

```python
class Project(models.Model, Noun):
    owners = models.ManyToManyField(Person)

    def get_verbs(self):
        verbs = [
            ProjectVerbs(self)
        ]
        return verbs
```

###Displaying in a Template

```html
<ul>
  {% for verb in noun.get_available_verbs %}
      <li><a href="{{ verb.url }}">{{ verb.display_name }}</a></li>
  {% endfor %}
</ul>
```

