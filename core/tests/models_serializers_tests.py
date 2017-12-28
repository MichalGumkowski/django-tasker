from model_mommy import mommy

from django.contrib.auth.models import User

from rest_framework.test import APITestCase

from core.models.comment import Comment
from core.models.notification import Notification
from core.models.task import Task
from core.models.team import Team

from core.serializer import TeamSerializer


class CommentTesting(APITestCase):

    def setUp(self):
        self.comment = mommy.make(Comment)

    def test_comment_creates_notification(self):
        notifications = [notification.text for notification in Notification.objects.all()]

        self.assertTrue(notifications != [])
        text = self.comment.creator.username + \
               " just added a comment to the task: " + \
                self.comment.task.title

        self.assertTrue(text in notifications)


class TaskTesting(APITestCase):
    def setUp(self):
        self.task = mommy.make(Task)
        self.task.is_finished = True
        self.task.save()

    def test_creating_task_creates_notification(self):
        notifications = [notification.text for notification in Notification.objects.all()]
        self.assertTrue(notifications != [])

        text = self.task.creator.username + " added a new task for you: <b>" + \
               self.task.title + ".</b>"

        self.assertTrue(text in notifications)

    def test_finishing_task_creates_notification(self):
        notifications = [notification.text for notification in Notification.objects.all()]
        self.assertTrue(notifications != [])

        text = self.task.target.username + " has finished his task: <b>" + \
               self.task.title + ".</b>"

        self.assertTrue(text in notifications)


class TeamTesting(APITestCase):
    def setUp(self):
        self.team = mommy.make(Team)
        self.user1 = mommy.make(User)
        self.user2 = mommy.make(User)
        self.user3 = mommy.make(User)

        self.user1.teams.add(self.team)
        self.user2.teams.add(self.team)

        team_members_pk = [member.pk for member in self.team.members.all()]

        data = {'name': self.team.name,
                'description': self.team.description,
                'members': self.team.members.all(),
                'tasks': self.team.tasks.all()
                }

        self.team_serializer = TeamSerializer(data=data)
        self.team_serializer.is_valid()

        validated_data = TeamSerializer.validate(self.team, attrs=data)
        self.team_serializer.create(validated_data=validated_data)
        #print(self.team_serializer.data)

    def test_user_receives_info_about_being_added_to_new_team(self):
        notifications = [notification.text for notification in Notification.objects.all()]
        self.assertTrue(notifications != [])

        text = "You have been added do the team <b>" + self.team.name + "</b>"
        self.assertTrue(text in notifications)


    def test_members_receives_info_about_user_being_added_to_existing_team(self):

        data_add = {'name': self.team.name,
                'description': self.team.description,
                'members': [self.user1, self.user2, self.user3],
                'tasks': self.team.tasks.all()
                }

        validated_data_add = TeamSerializer.validate(self.team, attrs=data_add)

        self.team_serializer.update(instance=self.team,
                              validated_data=validated_data_add)

        notifications = \
            [notification.text for notification in Notification.objects.all()]

        text_add = "<b>" + self.user3.username + "</b>" \
               " has been added to your team <b>" + \
               self.team.name + "</b>"

        text_user = "You have been added do the team <b>" + self.team.name + "</b>"

        self.assertTrue(text_add in notifications)
        self.assertTrue(text_user in notifications)

    def test_members_receive_info_about_user_being_removed_from_existing_team(self):
        data_remove = {'name': self.team.name,
                       'description': self.team.description,
                       'members': [self.user1, ],
                       'tasks': self.team.tasks.all()
                       }

        validated_data_remove = TeamSerializer.validate(self.team,
                                                        attrs=data_remove)

        self.team_serializer.update(instance=self.team,
                                    validated_data=validated_data_remove)

        notifications = \
            [notification.text for notification in Notification.objects.all()]

        text_remove = "<b>" + self.user2.username + "</b>" \
               " has been removed from your team <b>" + \
               self.team.name + "</b>"

        text_user = "You have been removed from your team <b>" + self.team.name + "</b>"

        self.assertTrue(text_remove in notifications)
        self.assertTrue(text_user in notifications)


