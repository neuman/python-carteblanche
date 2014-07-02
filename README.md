This readme will introduce you to Carteblanche and walk you through an example app, please refer to [carteblanche-django-starter](https://github.com/neuman/carteblanche-django-starter) for the full example project.

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


Guided Intro
------------

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

You would add the following to our verbs.py file.  You can see how easy it is to avoid running the same 'is_available' (by having SprocketUpdateVerb and SprocketUpdateVerb inherit from SprocketeerVerb they share a 'condition_name').

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

In order to make these Verbs actually work for us, you must link them to a Noun.  Make an existing model into a Noun by adding the mixin after models.Model in the inheritance chain, and adding a 'verb_classes' attribute as seen below.

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from carteblanche.base import Noun
from core.verbs import *

class Sprocket(models.Model, Noun):
    sprocketeers = models.ManyToManyField(User)
    title = models.CharField(max_length=300)
    verb_classes = [SprocketDetailVerb, SprocketUpdateVerb, SprocketListVerb]

    def __str__(self):
        return self.title

    def is_sprocketeer(self, user):
        return self.sprocketeers.filter(id=user.id).count() > 0

    def get_absolute_url(self):
        return SprocketDetailVerb(self).get_url()

```

Now that your model has become a Noun, any views pertaining to it need to become NounViews.  Add the NounView mixin before View in the inheritance chain.  You must also add a 'get_noun' function that returns the instance of the model this view pertains to.  Look how clean these views are!

```python
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from carteblanche.mixins import NounView
import core.models as cm

class SprocketView(NounView):

    def get_noun(self, **kwargs):
        return cm.Sprocket.objects.get(id=self.kwargs['pk'])


class SprocketDetailView(SprocketView, TemplateView):
    template_name = 'base.html'


class SprocketUpdateView(SprocketView, UpdateView):
    model = cm.Sprocket
    template_name = 'form.html'
    success_url = '/'

    def get_success_url(self):
        return cm.SprocketDetailVerb(self.noun).get_url()
```

At this point, all of the above views should automatically allow access to users who are members of a given sprocket and deny access to everyone else, but what about those other verbs we defined earlier that don't actually have a Noun?  SiteJoinVerb and SiteLoginVerb are actions pertaining to the site itself rather than a particular model, so we'll just create a Noun for the site along with a few more verbs that are available at the siteroot.  Add the following to your verbs.py file.

```python
class SprocketCreateVerb(CoreVerb):
    display_name = "Create New Sprocket"
    view_name='sprocket_create'
    condition_name = 'is_authenticated'
    required = True

    @availability_login_required
    def is_available(self, user):
        return True

class SprocketListVerb(AuthenticatedVerb):
    display_name = "List Sprockets"
    view_name = 'sprocket_list'

class SiteRoot(Noun):
    '''
    A convenient hack that lets pages that have no actual noun have verbs and verb-based permissions. 
    '''
    verb_classes = [SiteJoinVerb, SiteLoginVerb, SprocketCreateVerb]

    def __unicode__(self):
        return 'Site Root'

    class Meta:
        abstract = True
```

Now add the following to your views.py file.

```python

class SiteRootView(NounView):
    def get_noun(self, **kwargs):
        siteroot = cm.SiteRoot()
        return siteroot

class IndexView(SiteRootView, TemplateView):
    template_name = 'index.html'

#this login/user create stuff might be better off in a different app
class UserCreateView(SiteRootView, CreateView):
    model = User
    template_name = 'form.html'
    form_class = cf.RegistrationForm
    success_url = '/'

    def form_valid(self, form):
        user = User.objects.create_user(uuid4().hex, form.cleaned_data['email'], form.cleaned_data['password1'])
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['first_name']
        user.save()
        user = authenticate(username=user.username, password=form.cleaned_data['password1'])
        login(self.request, user)
        form.instance = user
        return super(UserCreateView, self).form_valid(form)


class UserLoginView(SiteRootView, FormView):
    template_name = 'form.html'
    form_class = cf.LoginForm
    success_url = '/'

    def form_valid(self, form):
        user = form.user_cache
        login(self.request, user)
        form.instance = user
        return super(UserLoginView, self).form_valid(form)    

class SprocketCreateView(SiteRootView, CreateView):
    model = cm.Sprocket
    template_name = 'form.html'
    form_class = cf.SprocketForm
    success_url = '/'

    def get_success_url(self):
        self.object.sprocketeers.add(self.request.user)
        return cm.SprocketDetailVerb(self.object).get_url()
```

###Displaying in a Template
The NounView mixin automatically includes 'available_verbs', 'conditions' and 'noun' in the cointext it hands to the template renderer.  All you have to do to display the dynamically rendered navigation menu is include the following somewhere in your template.
```html
<ul>
  {% for verb in noun.get_available_verbs %}
      <li><a href="{{ verb.url }}">{{ verb.display_name }}</a></li>
  {% endfor %}
</ul>
```

When view access is denied to a user, Carteblanche uses django's messaging system to display the appropriate Verb's 'denied_message'.  You can set 'MESSAGES_TEMPLATE' to a custom template in your settings file.  The messages template should include something similar to the following:

```html
{% for message in messages %}
    <div class="alert alert-{{ message.tags }}">{{ message }}</div>
{% endfor %}
```