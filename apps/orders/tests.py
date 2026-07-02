from django.test import TestCase

# Create your tests here.


class TestOrderLifesycle(TestCase):
    def setUp(self):

        self.UrlCreate = "/api/v1/orders/create/"
        self.UrlUpdate = "/api/v1/orders//"
