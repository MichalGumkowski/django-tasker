from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import django.dispatch
import datetime

from .task import *


class Comment(models.Model):

    creator = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    text = models.TextField(default="")

    comment_added = django.dispatch.Signal(providing_args=['creator', 'task',
                                                           'date', 'pk'])

    def __str__(self):
        return self.creator.username + '\'s comment to ' + \
                    self.task.title + ' task'

    #send notification when comment has been added
    def send_notification(self, instance):
        comment_created.send(sender=self.__class__, creator=instance.creator,
                             date=instance.date, pk=instance.pk)