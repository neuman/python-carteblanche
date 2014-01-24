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
        cache.__contains__('is_member')
        output = []
        for a in self.get_verbs():
            #availability key should be the same for verbs that have
            #the same is_available method
            if self.instance.availability_key != None:
                #if the key exists, the method has been run already so we skip it
                if cache.__contains__(self.instance.availability_key):
                    available = cache[self.instance.availability_key]
                else:
                    #otherwise we run the method and add it to the cache
                    available = a.is_available(user):
                    cache.__setitem__(self.instance.availability_key, available)
                if available == True:
                    output.append(a.get_serialized())
        return output

    def try_cache(self, key, value):
        if self.instance.noun_cache.__contains__('is_member'):
            print 'using data from cache'
            return self.instance.noun_cache['is_member']
        else:
            print 'add to cache'
            is_member = self.instance.members.filter(id=user.id).count() > 0
            self.instance.noun_cache.__setitem__('is_member',is_member)
        return is_member

    class Meta:
        abstract = True
