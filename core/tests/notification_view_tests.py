from model_mommy import mommy

from core.models.notification import Notification
from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class TeamViewsetTest(APITestCase):
    """ Testing TeamViewSet for working and permissions """

    def setUp(self):
        """ Setting up the tests """
        #Urls
        self.url = '/notifications/'
        self.instance_url = '/notifications/1/'
        self.oor_instance_url = '/notifications/999/'

        #Users
        self.user = mommy.make(User)
        self.user2 = mommy.make(User)

        #Notifications
        self.notification = mommy.make(Notification)
        self.user.notification.add(self.notification)

        self.notification2 = mommy.make(Notification)
        self.user2.notification.add(self.notification2)

    def login_user(self, user, what_for='list'):
        client = APIClient()
        client.force_authenticate(user)

        if what_for == 'list':
            return client.get(self.url)
        elif what_for == 'instance':
            return client.get(self.instance_url)
        elif what_for == 'oor_instance':
            return client.get(self.oor_instance_url)

    """ Notification List View Testing """
    def test_non_logged_user_cannot_access_user_notifications(self):
        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_user_can_access_his_notifications(self):
        response = self.login_user(self.user)

        self.assertEqual(response.status_code, 200)

    def test_view_shows_proper_notifications(self):
        response = self.login_user(self.user)

        response_notif = [notif['id'] for notif in response.data]
        user_notif = [notif.pk for notif in self.user.notification.all()]

        self.assertEqual(response_notif, user_notif)

    """ Notification Instance View Testing """
    def test_non_logged_user_cannot_access_user_notification_details(self):
        client = APIClient()
        response = client.get(self.instance_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_notification_details(self):
        response = self.login_user(self.user2, what_for='instance')

        self.assertEqual(response.status_code, 404)
        print(3)

    def test_user_can_access_his_notification_details(self):
        response = self.login_user(self.user, what_for='instance')

        print(3)
        self.assertEqual(response.status_code, 200)

