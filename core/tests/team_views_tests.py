from model_mommy import mommy

from core.models.team import Team
from core.models.task import Task
from core.models.comment import Comment
from django.contrib.auth.models import User

from rest_framework.test import APIClient, APITestCase


class TeamViewsetTest(APITestCase):
    """ Testing TeamViewSet for working and permissions """

    def setUp(self):
        """ Setting up the tests """
        #Urls
        self.url = '/teams/'
        self.instance_url = '/teams/1/'
        self.oor_instance_url = '/teams/999/'
        self.instance_users_url = '/teams/1/users/'
        self.instance_tasks_url = '/teams/1/tasks/'
        self.oor_instance_users_url = '/teams/999/users/'
        self.oor_instance_tasks_url = '/teams/999/tasks/'
        self.instance_task_detail_url = '/teams/1/tasks/1/'
        self.oor_instance_task_detail_url = '/teams/1/tasks/999/'
        self.instance_task_comments_url = '/teams/1/tasks/1/comments/'

        #users
        self.team_user = mommy.make(User)
        self.team_user_with_task = mommy.make(User)

        self.non_team_user = mommy.make(User)

        self.admin_user = mommy.make(User)
        self.admin_user.is_admin = True

        #team settings
        self.team = mommy.make(Team)
        self.team.members.add(self.team_user)
        self.team.members.add(self.team_user_with_task)

        self.empty_team = mommy.make(Team)

        #tasks
        self.task = mommy.make(Task)
        self.team.tasks.add(self.task)

        self.task_to_empty_team = mommy.make(Task)
        self.empty_team.tasks.add(self.task_to_empty_team)

        #comments
        self.comment = mommy.make(Comment)
        self.task.comments.add(self.comment)

        self.comment_to_another_task = mommy.make(Comment)
        self.task_to_empty_team.comments.add(self.comment_to_another_task)


    def login_user(self, user, what_for='list'):
        client = APIClient()
        client.force_authenticate(user)

        if what_for == 'list':
            return client.get(self.url)
        elif what_for == 'instance':
            return client.get(self.instance_url)
        elif what_for == 'oor_instance':
            return client.get(self.oor_instance_url)
        elif what_for == 'instance_users':
            return client.get(self.instance_users_url)
        elif what_for == 'instance_tasks':
            return client.get(self.instance_tasks_url)
        elif what_for == 'oor_instance_users':
            return client.get(self.oor_instance_users_url)
        elif what_for == 'oor_instance_tasks':
            return client.get(self.oor_instance_tasks_url)
        elif what_for == 'instance_task_details':
            return client.get(self.instance_task_detail_url)
        elif what_for == 'oor_instance_task_details':
            return client.get(self.oor_instance_task_detail_url)
        elif what_for == 'instance_task_comments':
            return client.get(self.instance_task_comments_url)


    """ Team List View Testing """
    def test_non_logged_user_cannot_access_teams(self):
        client = APIClient()
        response = client.get(self.url)

        self.assertEqual(response.status_code, 401)

    def test_non_team_user_can_access_teams(self):
        response = self.login_user(self.non_team_user)

        self.assertEqual(response.status_code, 200)

    def test_team_user_can_access_teams(self):
        response = self.login_user(self.team_user)

        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_teams(self):
        response = self.login_user(self.admin_user)

        self.assertEqual(response.status_code, 200)

    """ Team Instance General View Testing """
    def test_non_logged_user_cannot_access_team_instance(self):
        client = APIClient()
        response = client.get(self.instance_url)

        self.assertEqual(response.status_code, 401)

    def test_non_team_user_can_access_team_instance(self):
        response = self.login_user(self.non_team_user, what_for='instance')

        self.assertEqual(response.status_code, 200)

    def test_team_user_can_access_team_instance(self):
        response = self.login_user(self.team_user, what_for='instance')

        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_team_instance(self):
        response = self.login_user(self.admin_user, what_for='instance')

        self.assertEqual(response.status_code, 200)

    def test_view_shows_proper_team_members(self):
        response = self.login_user(self.team_user, what_for='instance')
        response_team_members = response.data['members']

        team_members = [member.id for member in self.team.members.all()]

        self.assertEqual(response_team_members, team_members)

    def test_view_shows_proper_team_tasks(self):
        response = self.login_user(self.team_user, what_for='instance')
        response_tasks = response.data['tasks']
        team_tasks = [task.id for task in self.team.tasks.all()]

        self.assertEqual(response_tasks, team_tasks)


    """ Team instance out of range testing """
    def test_non_logged_user_out_of_range_instance(self):
        client = APIClient()
        response = client.get(self.oor_instance_url)

        self.assertEqual(response.status_code, 401)

    def test_logged_user_out_of_range_instance(self):
        response = self.login_user(self.team_user, what_for='oor_instance')

        self.assertEqual(response.status_code, 404)

    """ Team instance detailed view testing (users) """
    def test_non_logged_user_cannot_access_team_instance_users_list(self):
        client = APIClient()
        response = client.get(self.instance_users_url)

        self.assertEqual(response.status_code, 401)

    def test_non_team_user_cannot_access_team_instance_users_list(self):
        response = self.login_user(self.non_team_user,
                                   what_for='instance_users')

        self.assertEqual(response.status_code, 403)

    def test_team_user_can_access_team_instance_users_list(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_users')

        self.assertEqual(response.status_code, 200)

    def test_team_instance_users_list_returns_proper_users(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_users')
        response_users = [user['id'] for user in response.data]

        team_users = [member.id for member in self.team.members.all()]

        self.assertEqual(response_users, team_users)

    def test_team_instance_ouf_of_range_users(self):
        response = self.login_user(self.team_user,
                                   what_for='oor_instance_users')

        self.assertEqual(response.status_code, 404)

    """ Team instance detailed view testing (tasks) """

    def test_non_logged_user_cannot_access_team_instance_tasks_list(self):
        client = APIClient()
        response = client.get(self.instance_tasks_url)

        self.assertEqual(response.status_code, 401)

    def test_non_team_user_cannot_access_team_instance_tasks_list(self):
        response = self.login_user(self.non_team_user,
                                   what_for='instance_tasks')

        self.assertEqual(response.status_code, 403)

    def test_team_user_can_access_team_instance_tasks_list(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_tasks')

        self.assertEqual(response.status_code, 200)

    def test_team_instance_tasks_list_returns_proper_tasks(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_tasks')
        response_tasks = [task['pk'] for task in response.data]

        team_tasks = [task.pk for task in self.team.tasks.all()]

        self.assertEqual(response_tasks, team_tasks)

    def test_team_instance_ouf_of_range_tasks(self):
        response = self.login_user(self.team_user,
                                   what_for='oor_instance_tasks')

        self.assertEqual(response.status_code, 404)

    """ Team instance detailed view testing (task instance) """
    def test_non_logged_user_cannot_access_team_instance_task_details(self):
        client = APIClient()
        response = client.get(self.instance_tasks_url)

        self.assertEqual(response.status_code, 401)

    def test_non_team_user_cannot_access_team_instance_task_details(self):
        response = self.login_user(self.non_team_user,
                                   what_for='instance_task_details')

        self.assertEqual(response.status_code, 403)

    def test_team_user_can_access_team_instance_task_details(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_task_details')

        self.assertEqual(response.status_code, 200)

    def test_team_instance_task_details_returns_proper_task(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_task_details')

        self.assertEqual(response.data['pk'], self.task.pk)

    def test_team_instance_task_details_out_of_range(self):
        response = self.login_user(self.team_user,
                                   what_for='oor_instance_task_details')

        self.assertEqual(response.status_code, 404)

    """ Team instance detailed view testing (task instance comments) """
    def test_non_logged_user_cannot_access_team_instance_task_comments(self):
        client = APIClient()
        response = client.get(self.instance_task_comments_url)

        self.assertEqual(response.status_code, 401)

    def test_non_team_user_cannot_access_team_instance_task_comments(self):
        response = self.login_user(self.non_team_user,
                                   what_for='instance_task_comments')

        self.assertEqual(response.status_code, 403)

    def test_team_user_can_access_team_instance_task_comments(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_task_comments')

        self.assertEqual(response.status_code, 200)

    def test_team_instance_task_comments_returns_proper_comments(self):
        response = self.login_user(self.team_user,
                                   what_for='instance_task_details')
        response_comments = [comment for comment in response.data['comments']]

        task_comments = [comment.pk for comment in self.task.comments.all()]

        print(5)
        self.assertEqual(response_comments, task_comments)