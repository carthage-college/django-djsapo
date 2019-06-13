from django.conf import settings
from django.test import TestCase
from django.contrib.auth.models import User

from djsapo.core.models import Alert

from djtools.utils.logging import seperator

from unittest import skip


@skip("skip for now")
class CoreModelsAlertTestCase(TestCase):

    fixtures = [ 'user.json','profile.json', ]

    def setUp(self):

        self.user = User.objects.get(pk=settings.TEST_USER_ID)

    def test_message(self):
        print("\n")
        print("create an Alert object")
        seperator()
        alert = Alert.objects.create()
