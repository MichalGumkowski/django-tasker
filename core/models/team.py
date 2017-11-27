from django.db import models
from django.contrib.auth.models import User


class Team(models.Model):

    name = models.CharField(
        max_length=200,
        null=False,
        blank=False
    )

    description = models.TextField()

    members = models.ManyToManyField(
        User
    )