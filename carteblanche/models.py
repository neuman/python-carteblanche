from django.core.urlresolvers import reverse

class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between verb-urls, objects, and users.
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

    class Meta:
        abstract = True


class Noun(object):
    noun_cache = {}
    '''
    Mixin intended to operate with Verb, most likely in a django-like Model or class-based View.
    '''
    def get_verbs(self):
        return []

    def get_available_verbs(self, user):
        output = []
        for a in self.get_verbs():
            if a.is_available(user):
                output.append(a.get_serialized())
        return output

    class Meta:
        abstract = True
