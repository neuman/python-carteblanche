import carteblanche.base as cb
from django.views.generic import DetailView
from django.shortcuts import render_to_response
from django.core.urlresolvers import resolve
from django.template import RequestContext
from django.core.urlresolvers import reverse
from functools import wraps
from django.utils.decorators import available_attrs
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

class NounView(SuccessMessageMixin):
    success_message = "That worked!"

    def __init__(self, **kwargs):
        super(NounView, self).__init__(**kwargs)
        self.noun = None
        
    def get_view_required_verbs(self, view_name):
        verbs = []
        for v in self.noun.get_verbs():
            if v.required == True:
                if v.view_name == view_name:
                    verbs.append(v)
        return verbs

    def get_view_required_unavailable_verbs(self, view_name, user):
        verbs = []
        for v in self.get_view_required_verbs(view_name):
            if not v.is_available(user):
                verbs.append(v)
        return verbs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(NounView, self).get_context_data(**kwargs)
        available_verbs = self.noun.get_available_verbs(self.request.user)
        context['available_verbs'] = available_verbs
        context['conditions'] = self.noun.conditions.get_available(self.request.user)
        self.noun.conditions.cache = {}
        return context

    def dispatch(self, *args, **kwargs):
        self.noun = self.get_noun(**kwargs)
        #what verbs are required and available for viewing of this page
        #for each of those, get a forbidden message and direct the user to a messaging view
        view_name = resolve(self.request.path_info).url_name
        denied_messages = []
        for verb in self.get_view_required_unavailable_verbs(view_name, self.request.user):
            denied_messages.append(verb.denied_message)
        if len(denied_messages) > 0:
            for message in denied_messages:
                messages.add_message(self.request, messages.ERROR, message)
            return render_to_response('messages.html',{"available_verbs":self.noun.get_available_verbs(self.request.user)}, RequestContext(self.request))
        
        return super(NounView, self).dispatch(*args, **kwargs)

    class Meta:
        abstract = True

class DjangoVerb(cb.Verb):
    view_name = None
    app = None
    visible = True

    def get_url(self):
        '''
        Default django get_url for urls that require no args.
        '''
        return reverse(viewname=self.view_name, current_app=self.app)

def availability_login_required(is_available_func):
    @wraps(is_available_func, assigned=available_attrs(is_available_func))
    def decorator(self, user):
        print user
        if user.is_authenticated(): 
            return is_available_func(self, user)
        else:
            self.denied_message = "You must be logged in to "+self.display_name+"."
            return False
    return decorator