
from django.test import TestCase
from django.core.exceptions import ValidationError
from schema.models import Schema
from django.core.management import call_command
from django.contrib.auth.models import User, Group, Permission
from django.core.validators import MaxLengthValidator
from mixer.backend.django import mixer
import unittest
from django.contrib.auth.models import User

class TestModels(TestCase):
    

    def create_example_schema(self, schema_id = 1, issue = "for lite kaffe", content = "veldig viktig tekst"):
        #create user for the schema
        new_user = User.objects.create_user("test_user")


        return Schema.objects.create(schema_id = schema_id, issue=issue, poster = new_user, content = content)

    def test_object(self):  
        s = self.create_example_schema()
        self.assertTrue(isinstance(s,Schema))

    def test_schema_issue_valid(self):
        # schema = mixer.blend('schema.Schema', issue='for lite kaffe')
        s = self.create_example_schema()
        self.assertEquals(s.issue,'for lite kaffe')

    def test_schema_char_length(self):
        with self.assertRaises(ValidationError):
            s = self.create_example_schema(issue = "s"*101)
            Validate_issue(len(s.issue))
        
    


def Validate_issue(value):
    if(value > 100):
        raise ValidationError('error')