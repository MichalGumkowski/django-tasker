from model_mommy import mommy

from core.models.task import Task
from core.models.team import Team
from core.models.comment import Comment
from core.models.notification import Notification
from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class UserViewsetTest(APITestCase):

    def setUp(self):
        """ Setting up the tests """
        #Urls
        self.url = '/users/'
        self.instance_url = '/users/1/'
        self.oor_instance_url = '/users/999/'
        self.instance_teams_url = '/users/1/teams/'
        self.instance_tasks_url = '/users/1/tasks/'
        self.instance_notifications_url = '/users/1/notifications/'
        self.oor_instance_teams_url = '/users/999/teams/'
        self.oor_instance_tasks_url = '/users/999/tasks/'
        self.instance_task_detail_url = '/users/1/tasks/1/'
        self.oor_instance_task_detail_url = '/users/1/tasks/999/'
        self.instance_task_comments_url = '/users/1/tasks/1/comments/'

        #Users
        self.user = mommy.make(User)
        self.user2 = mommy.make(User)

        #Teams
        self.team = mommy.make(Team)
        self.team.members.add(self.user)
        self.team.members.add(self.user2)

        self.empty_team = mommy.make(Team)

        #Tasks
        self.task = mommy.make(Task)
        self.user.assigned_tasks.add(self.task)
        self.team.tasks.add(self.task)

        self.task2 = mommy.make(Task)
        self.user2.assigned_tasks.add(self.task2)
        self.team.tasks.add(self.task2)

        #Comments
        self.comment = mommy.make(Comment)
        self.task.comments.add(self.comment)

        self.comment2 = mommy.make(Comment)
        self.task2.comments.add(self.comment2)

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
        elif what_for == 'instance_teams':
            return client.get(self.instance_teams_url)
        elif what_for == 'instance_tasks':
            return client.get(self.instance_tasks_url)
        elif what_for == 'instance_notification':
            return client.get(self.instance_notifications_url)
        elif what_for == 'oor_instance_teams':
            return client.get(self.oor_instance_teams_url)
        elif what_for == 'oor_instance_tasks':
            return client.get(self.oor_instance_tasks_url)
        elif what_for == 'instance_task_details':
            return client.get(self.instance_task_detail_url)
        elif what_for == 'oor_instance_task_details':
            return client.get(self.oor_instance_task_detail_url)
        elif what_for == 'instance_task_comments':
            return client.get(self.instance_task_comments_url)


    """ Users List View Testing """
    def test_non_logged_user_cannot_access_users(self):
        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_user_can_access_his_tasks(self):
        response = self.login_user(self.user)

        self.assertEqual(response.status_code, 200)

    def test_view_shows_proper_all_users(self):
        response = self.login_user(self.user)
        response_users = [user['id'] for user in response.data]
        users = [user.id for user in User.objects.all()]
        self.assertEqual(response_users, users)

    """ Users Instance general testing """
    def test_non_logged_user_cannot_access_user_instance(self):
        client = APIClient()
        response = client.get(self.instance_url)

        self.assertEqual(response.status_code, 401)

    def test_logged_user_can_access_user_instance(self):
        response = self.login_user(self.user2, what_for='instance')

        self.assertEqual(response.status_code, 200)

    def test_logged_user_out_of_range_instance(self):
        response = self.login_user(self.user2, what_for='oor_instance')

        self.assertEqual(response.status_code, 404)

    """ Users Instance General Testing (notifications) """
    def test_non_logged_user_cannot_access_user_notifications(self):
        client = APIClient()
        response = client.get(self.instance_notifications_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_notifications(self):
        response = self.login_user(self.user2, what_for='instance_notification')

        self.assertEqual(response.status_code, 403)

    def test_user_can_access_user_notification(self):
        response = self.login_user(self.user, what_for='instance_notification')

        self.assertEqual(response.status_code, 200)

    def test_user_notification_returns_proper_data(self):
        response = self.login_user(self.user, what_for='instance_notification')
        response_notifications = [notification['id'] for notification in response.data]

        user_notifications = [notification.pk for notification in self.user.notification.all()]

        self.assertEqual(response_notifications, user_notifications)

    """ Users Instance General Testing (tasks) """
    def test_non_logged_user_cannot_access_user_tasks(self):
        client = APIClient()
        response = client.get(self.instance_tasks_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_tasks(self):
        response = self.login_user(self.user2, what_for='instance_tasks')

        self.assertEqual(response.status_code, 403)

    def test_user_can_access_user_tasks(self):
        response = self.login_user(self.user, what_for='instance_tasks')

        self.assertEqual(response.status_code, 200)

    def test_user_tasks_returns_proper_data(self):
        response = self.login_user(self.user, what_for='instance_tasks')
        response_tasks = [task['pk'] for task in response.data]

        user_tasks = [task.pk for task in self.user.assigned_tasks.all()]

        self.assertEqual(response_tasks, user_tasks)

    """ Users Instance General Testing (teams) """

    def test_non_logged_user_cannot_access_user_teams(self):
        client = APIClient()
        response = client.get(self.instance_teams_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_teams(self):
        response = self.login_user(self.user2, what_for='instance_teams')

        self.assertEqual(response.status_code, 403)

    def test_user_can_access_user_teams(self):
        response = self.login_user(self.user, what_for='instance_teams')

        self.assertEqual(response.status_code, 200)

    def test_user_teams_returns_proper_data(self):
        response = self.login_user(self.user, what_for='instance_teams')
        response_teams = [team['name'] for team in response.data]

        user_teams = [team.name for team in self.user.teams.all()]

        self.assertEqual(response_teams, user_teams)

    """ Users Instance General Testing (oor_teams, oor_tasks, oor_notifications) """
    def test_another_user_oor_user_sth(self):
        response = self.login_user(self.user2, what_for='oor_instance_teams')

        self.assertEqual(response.status_code, 404)

    def test_user_oor_user_sth(self):
        response = self.login_user(self.user, what_for='oor_instance_teams')

        self.assertEqual(response.status_code, 404)

    """ Users Instance General Testing (User task details) """
    def test_non_logged_user_cannot_access_user_task_details(self):
        client = APIClient()
        response = client.get(self.instance_task_detail_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_task_details(self):
        response = self.login_user(self.user2, what_for='instance_task_details')

        self.assertEqual(response.status_code, 403)

    def test_user_can_access_user_user_task_details(self):
        response = self.login_user(self.user, what_for='instance_task_details')

        self.assertEqual(response.status_code, 200)

    def test_user_task_details_returns_proper_data(self):
        response = self.login_user(self.user, what_for='instance_task_details')
        response_details = response.data['pk']

        task_details = self.task.pk

        self.assertEqual(response_details, task_details)

    """ Users Instance General Testing (oor_teams, oor_tasks, oor_notifications) """
    def test_another_user_oor_task_details(self):
        response = self.login_user(self.user2, what_for='oor_instance_task_details')

        self.assertEqual(response.status_code, 403)

    def test_user_oor_task_details(self):
        response = self.login_user(self.user, what_for='oor_instance_task_details')

        self.assertEqual(response.status_code, 404)

    """ Users Instance General Testing (User task details) """
    def test_non_logged_user_cannot_access_user_task_comments(self):
        client = APIClient()
        response = client.get(self.instance_task_comments_url)

        self.assertEqual(response.status_code, 401)

    def test_another_user_cannot_access_user_task_comments(self):
        response = self.login_user(self.user2, what_for='instance_task_comments')

        self.assertEqual(response.status_code, 403)

    def test_user_can_access_user_user_task_comments(self):
        response = self.login_user(self.user, what_for='instance_task_comments')

        print(6)
        self.assertEqual(response.status_code, 200)
