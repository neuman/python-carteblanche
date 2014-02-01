import carteblanche.models as cb
from django.views.generic import DetailView
from django.shortcuts import render_to_response
from django.core.urlresolvers import resolve
from django.template import RequestContext


class NounView(object):
    noun = None

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
        context = super(RequiredVerbsAvailable, self).get_context_data(**kwargs)
        context['available_verbs'] = self.noun.get_available_verbs(self.request.user)
        return context

    def dispatch(self, *args, **kwargs):
    	#raise Exception('reached')
        if self.noun == None:
            self.noun = self.get_noun(**kwargs)
        #what verbs are required and available for viewing of this page
        #for each of those, get a forbidden message and direct the user to a messaging view
        view_name = resolve(self.request.path_info).url_name
        denied_messages = []
        for verb in self.get_view_required_unavailable_verbs(view_name, self.request.user):
            denied_messages.append(verb.denied_message)
        if len(denied_messages) > 0:
            return render_to_response('messages.html',{"messages":denied_messages, "available_verbs":self.noun.get_available_verbs(self.request.user)}, RequestContext(self.request))
        
        return super(RequiredVerbsAvailable, self).dispatch(*args, **kwargs)

    class Meta:
        abstract = True

class DjangoVerb(cb.verb):
    view_name='pledge_create'
    login_required = False

    def is_available(self, person):
        "takes a user and always returns True or False"
        return True