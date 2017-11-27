from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import django.dispatch
import datetime


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