from model_mommy import mommy

from core.models.team import Team
from core.models.task import Task
from core.models.comment import Comment
from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class TaskViewsetTest(APITestCase):

    def setUp(self):
        #Urls
        self.url = '/tasks/'
        self.instance_url = '/tasks/1/'
        self.oor_instance_url = '/tasks/999/'
        self.instance_comments_url = '/tasks/1/comments/'
        self.oor_instance_comments_url = '/tasks/999/comments/'

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


    def login_user(self, user, what_for='list'):
        client = APIClient()
        client.force_authenticate(user)

        if what_for == 'list':
            return client.get(self.url)
        elif what_for == 'instance':
            return client.get(self.instance_url)
        elif what_for == 'oor_instance':
            return client.get(self.oor_instance_url)
        elif what_for == 'instance_comments':
            return client.get(self.instance_comments_url)
        elif what_for == 'oor_instance_comments':
            return client.get(self.oor_instance_comments_url)


    """ Tasks List View Testing """
    def test_non_logged_user_cannot_access_user_tasks(self):
        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, 403)

    def test_user_can_access_his_tasks(self):
        response = self.login_user(self.user)

        self.assertEqual(response.status_code, 200)

    def test_view_shows_proper_tasks(self):
        response = self.login_user(self.user)

        response_tasks = [task['pk'] for task in response.data]
        user_tasks = [task.pk for task in self.user.assigned_tasks.all()]

        self.assertEqual(response_tasks, user_tasks)

    """ Tasks Instance Testing """
    def test_non_logged_user_cannot_access_user_task_details(self):
        client = APIClient()
        response = client.get(self.instance_url)

        self.assertEqual(response.status_code, 403)

    def test_another_user_cannot_access_user_task_details(self):
        response = self.login_user(self.user2, what_for='instance')

        self.assertEqual(response.status_code, 404)

    def test_user_can_access_his_task_details(self):
        response = self.login_user(self.user, what_for='instance')

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_oor_task_details(self):
        response = self.login_user(self.user, what_for='oor_instance')

        self.assertEqual(response.status_code, 404)

    """ Tasks Instance Testing (comments) """
    def test_non_logged_user_cannot_access_user_task_comments(self):
        client = APIClient()
        response = client.get(self.instance_comments_url)

        self.assertEqual(response.status_code, 403)

    def test_another_user_cannot_access_user_task_comments(self):
        response = self.login_user(self.user2, what_for='instance_comments')

        self.assertEqual(response.status_code, 404)

    def test_user_can_access_his_task_comments(self):
        response = self.login_user(self.user, what_for='instance_comments')

        self.assertEqual(response.status_code, 200)

    def test_user_cannot_access_oor_task_comments(self):
        response = self.login_user(self.user, what_for='oor_instance_comments')
        print(4)

        self.assertEqual(response.status_code, 404)