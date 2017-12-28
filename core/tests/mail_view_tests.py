from model_mommy import mommy

from core.models.mail import Mail
from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class MailViewsetTest(APITestCase):

    def setUp(self):
        """ Setting up the tests """
        #Urls
        self.url = '/mails/'
        self.instance_url = '/mails/1/'
        self.oor_instance_url = '/mails/999/'

        #Users
        self.user = mommy.make(User)
        self.user2 = mommy.make(User)
        self.admin_user = mommy.make(User)
        self.admin_user.is_staff = True

        #Mails
        self.mail = mommy.make(Mail)
        self.user.mails.add(self.mail)

        self.mail2 = mommy.make(Mail)
        self.user.mails.add(self.mail2)

    def login_user(self, user, what_for='list'):
        client = APIClient()
        client.force_authenticate(user)

        if what_for == 'list':
            return client.get(self.url)
        elif what_for == 'instance':
            return client.get(self.instance_url)
        elif what_for == 'oor_instance':
            return client.get(self.oor_instance_url)

    """ Mail List View Testing """
    def test_non_logged_user_cannot_access_mails(self):
        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_mails(self):
        response = self.login_user(self.user2)

        self.assertEqual(response.status_code, 403)

    def test_user_cannot_access_his_mails(self):
        response = self.login_user(self.user)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_mails(self):
        response = self.login_user(self.admin_user)

        self.assertEqual(response.status_code, 200)

    def test_view_shows_proper_mails(self):
        response = self.login_user(self.admin_user)

        response_mails = [mail['text'] for mail in response.data]
        user_mails = [mail.text for mail in Mail.objects.all()]

        self.assertEqual(response_mails, user_mails)

    """ Mail Instance View Testing """
    def test_non_logged_user_cannot_access_mail_instance(self):
        client = APIClient()
        response = client.get(self.instance_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_mail_instance(self):
        response = self.login_user(self.user2, what_for='instance')

        self.assertEqual(response.status_code, 403)

    def test_user_cannot_access_his_mail_instance(self):
        response = self.login_user(self.user, what_for='instance')

        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_mail_instance(self):
        response = self.login_user(self.admin_user, what_for='instance')

        self.assertEqual(response.status_code, 200)

    def test_view_shows_proper_mail_instance(self):
        response = self.login_user(self.admin_user, what_for='instance')

        response_mails = response.data['text']
        user_mails = Mail.objects.filter(pk=1)[0].text

        self.assertEqual(response_mails, user_mails)

    def test_user_cannot_access_oor_mail_instance(self):
        response = self.login_user(self.user, what_for='oor_instance')

        self.assertEqual(response.status_code, 403)

    def test_admin_cannot_access_oor_mail_instance(self):
        response = self.login_user(self.admin_user, what_for='oor_instance')

        self.assertEqual(response.status_code, 404)