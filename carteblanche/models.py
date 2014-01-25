
class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between verb-urls, objects, and users.
    '''
    url = "Unspecified"
    display_name = "Unspecified"
    availability_key = None

    def __init__(self, noun=None):
        self.noun = noun

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
    verb_classes = []
    def get_verbs(self):
        output = []
        for verb_class in self.verb_classes:
            output.append(verb_class(self))
        return output

    def get_available_verbs(self, user):
        cache = {}
        output = []
        for a in self.get_verbs():
            #availability key should be the same for verbs that have
            #the same is_available method
            try:
                available = cache[a.availability_key]
            except Exception as e:
                #otherwise we run the method and add it to the cache if it has a caching key
                available = a.is_available(user)
                if a.availability_key != None:
                    cache.__setitem__(a.availability_key, available)

            if available == True:
                output.append(a.get_serialized())
        return output

    class Meta:
        abstract = True

