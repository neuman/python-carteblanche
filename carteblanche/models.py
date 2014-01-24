from django.core.urlresolvers import reverse

class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between verb-urls, objects, and users.
    '''
    url = "Unspecified"
    display_name = "Unspecified"
    availability_key = None

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
    '''
    Mixin intended to operate with Verb, most likely in a django-like Model or class-based View.
    '''
    def get_verbs(self):
        return []

    def get_available_verbs(self, user):
        cache = {}
        output = []
        for a in self.get_verbs():
            #availability key should be the same for verbs that have
            #the same is_available method
            if a.availability_key != None:
                #if the key exists, the method has been run already so we skip it
                if cache.__contains__(a.availability_key):
                    available = cache[a.availability_key]
                else:
                    #otherwise we run the method and add it to the cache
                    available = a.is_available(user)
                    cache.__setitem__(a.availability_key, available)
                if available == True:
                    output.append(a.get_serialized())
        return output

    class Meta:
        abstract = True
