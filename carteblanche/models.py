from django.core.urlresolvers import reverse

class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between urls and objects and users.
    '''
    url = "Unspecified"
    display_name = "Unspecified"

    def __init__(self, instance=None):
        self.instance = instance

    def get_url(self):
        return self.url

    def get_display_name(self):
        return self.display_name

    def is_available(self, person):
        "takes a user and always returns True or False"
        return True

    def get_serialized(self):
        return {
            "url":self.get_url(),
            "display_name":self.get_display_name()
        }


class Noun(object):
    noun_cache = {}
    '''
    Mixin intended to operate with Action, most likely in a django Model or View.
    '''
    def get_actions(self):
        return []

    def get_available_actions(self, user):
        output = []
        for a in self.get_actions():
            if a.is_available(user):
                output.append(a.get_serialized())
        return output

    class Meta:
        abstract = True
