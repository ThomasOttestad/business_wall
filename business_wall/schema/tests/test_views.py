from django.test import TestCase, Client
from django.urls import reverse
from schema.models import Schema


class TestViews(TestCase):

    def test_create_schema(self):
        client = Client()
        response = client.get(reverse('list'))

        self.assertEquals(response.status_code, 200)
