from model_mommy import mommy

from .models.team import Team
from django.contrib.auth.models import User

from django.test import TestCase, Client


class TeamViewsetTest(TestCase):
    """Testing TeamViewSet for working and permissions"""

    def setUp(self):
        """
        Setting up the tests
        """
        self.team = mommy.make(Team)
        self.teamUser = mommy.make(
            User,
        )
        self.team.members = {'self.teamUser', }
        self.nonTeamUser = mommy.make(User)

    def check_if_team_user_can_access_teams(self):
        client = Client()
        client.login(username='self.teamUser.username',
                     password='self.teamUser.password')
        response = self.client.get()



