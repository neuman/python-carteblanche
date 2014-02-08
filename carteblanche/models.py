class Verb(object):
    '''
    Object to hold and serialize the in-memory relationship between verb-urls, objects, and users.
    '''
    url = "Unspecified"
    display_name = "Unspecified"
    denied_message = "Sorry dude, I'm afraid you can't do that."
    condition_name = None
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
        self.conditions = {}

    def get_verbs(self):
        '''
        Returns the full list of verbs registered on this noun regardless of availability. 
        '''
        output = []
        for verb_class in self.verb_classes:
            output.append(verb_class(self))
        return output

    def reset_conditions(self):
        '''
        Resets the cache entirely.
        '''
        self.conditions = {}

    def reset_condition(self, condition_name):
        '''
        Remove a single condition from the cache. 
        '''
        self.conditions.__delitem__(condition_name)

    def set_condition(self, condition_name, value):
        if type(value) != bool:
            raise Exception("key availability value must be bool")
        self.conditions.__setitem__(condition_name , value)

    def get_condition(self, user, condition_name):
        #prevent caching errors caused by None being used as a key
        if condition_name == None:
            raise Exception('condition_name cannot be None')

        #check the cache for a key lazily
        try:
            return self.conditions[condition_name]
        except Exception as e:
            #otherwise run the method and add it to the cache if it has a caching key
            for v in self.get_verbs():
                if v.condition_name == condition_name:
                    available = v.is_available(user)
                    self.set_condition(v.condition_name, available)
                    return available

    def get_available_verbs(self, user):
        '''
        Returns the list of verbs availabile to a specific user. 
        '''
        output = []
        for v in self.get_verbs():
            #availability key should be the same for verbs that have
            #the same is_available method
            if v.condition_name == None:
                available = v.is_available(user)
            else:
                available = self.get_condition(user, v.condition_name)

            if available == True:
                output.append(v.get_serialized())
        return output
