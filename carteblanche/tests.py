import random
import unittest
import models as cb


class Project(cb.Noun):
    run_count = 0

    def is_member(self, user):
        print "running is_member"
        self.run_count += 1
        return True

    def get_verbs(self):
        verbs = [
            ProjectUploadVerb(instance=self),
            ProjectPostVerb(instance=self),
            ProjectViewVerb(instance=self)
        ]
        return verbs

class ProjectViewVerb(cb.Verb):
    def get_url(self):
        return r"projects/"

class ProjectMemberVerb(cb.Verb):
    availability_key = "is_member"
    def is_available(self, user):
        return self.instance.is_member(user)

class ProjectUploadVerb(ProjectMemberVerb):
    display_name = "Upload Media"

    def get_url(self):
        return r"projects/upload"

class ProjectPostVerb(ProjectMemberVerb):
    display_name = "Post"

    def get_url(self):
        return "/projects/post"


class TestNounFunctions(unittest.TestCase):
    verbs = []
    nouns = []

    def setUp(self):
        self.nouns.append(Project())
        self.verbs.append(ProjectUploadVerb(self.nouns[0]))
        self.verbs.append(ProjectPostVerb(self.nouns[0]))
        self.verbs.append(ProjectViewVerb(self.nouns[0]))

    def test_cache(self):
        # make sure the is_member method was run once only
        self.nouns[0].get_available_verbs(None)
        self.assertTrue(self.nouns[0].run_count == 1)
        #reset it
        self.nouns[0].run_count = 0

    def test_no_cache(self):
    	verbs = self.nouns[0].get_available_verbs(None)
    	self.assertTrue(self.verbs[2].get_serialized() in verbs)


if __name__ == '__main__':
    unittest.main()
