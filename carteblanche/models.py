
class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between verb-urls, objects, and users.
    '''
    url = "Unspecified"
    display_name = "Unspecified"
    denied_message = "Sorry dude, I'm afraid you can't do that."
    availability_key = None
    required = True

    def __init__(self, noun=None):
        self.noun = noun

    def get_url(self):
        '''
        Returns the url associated with this verb.
        '''
        return self.url

    def get_display_name(self):
        return self.display_name

    def is_available(self, user):
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

    def __init__(self):
        #make sure the cache is empty and no one has messed with the class in memory
        #re-implement this once the caching bug is understood as a check
        #assert self.carteblanche_cache == {}
        self.carteblanche_cache = {}

    def get_verbs(self):
        '''
        Returns the full list of verbs registered on this noun regardless of availability. 
        '''
        output = []
        for verb_class in self.verb_classes:
            output.append(verb_class(self))
        return output

    def invalidate_carteblanche_cache(self):
        '''
        Resets the cache entirely.
        '''
        self.carteblanche_cache = {}

    def invalidate_availability_key(self, availability_key):
        '''
        Remove a single availability_key from the cache. 
        '''
        self.carteblanche_cache.__delitem__(availability_key)

    def set_key_availability(self, availability_key, value):
        if value != (True or False):
            raise Exception("key availability value must be bool")
        self.carteblanche_cache.__setitem__(availability_key , value)

    def get_key_availability(self, user, availability_key):
        #prevent caching errors caused by None being used as a key
        if availability_key == None:
            raise Exception('availability_key cannot be None')

        #check the cache for a key lazily
        try:
            return self.carteblanche_cache[availability_key]
        except Exception as e:
            #otherwise run the method and add it to the cache if it has a caching key
            for v in self.get_verbs():
                if v.availability_key == availability_key:
                    available = v.is_available(user)
                    self.set_key_availability(v.availability_key, available)
                    return available

    def get_available_verbs(self, user):
        '''
        Returns the list of verbs availabile to a specific user. 
        '''
        print "get_available_verbs"
        print type(self)
        output = []
        for v in self.get_verbs():
            #availability key should be the same for verbs that have
            #the same is_available method
            if v.availability_key == None:
                available = v.is_available(user)
            else:
                available = self.get_key_availability(user, v.availability_key)

            if available == True:
                output.append(v.get_serialized())
        return output
