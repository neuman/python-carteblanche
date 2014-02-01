
class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between verb-urls, objects, and users.
    '''
    url = "Unspecified"
    display_name = "Unspecified"
    denied_message = "Sorry dude, I'm afraid you can't do that."
    availability_key = None
    required = False

    def __init__(self, noun=None):
        self.noun = noun

    def get_url(self):
        '''
        Returns the url associated with this verb.
        '''
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
    carteblanche_cache = {}

    def get_verbs(self):
        '''
        Returns the full list of verbs registered on this noun regardless of availability. 
        '''
        output = []
        for verb_class in self.verb_classes:
            output.append(verb_class(self))
        return output

    def get_key_availability(self, user, availability_key):
        #prevent caching errors caused by None being used as a key
        if availability_key == None:
            raise Exception('availability_key cannot be None')

        #check the cache for a key lazily
        try:
            available = self.carteblanche_cache[availability_key]
        except Exception as e:
            #otherwise run the method and add it to the cache if it has a caching key
            for v in self.get_verbs():
                if v.availability_key == availability_key:
                    available = v.is_available(user)
                    self.carteblanche_cache.__setitem__(v.availability_key, available)
                    return available

    def get_available_verbs(self, user):
        '''
        Returns the list of verbs availabile to a specific user. 
        '''
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
