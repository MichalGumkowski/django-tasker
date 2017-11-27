from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import django.dispatch
import datetime

# Create your models here.

PROGRESS_CHOICES = (
    ('ASSIGNED', 'assigned'),
    ('IN_PROGRESS', 'in progress'),
    ('TESTED', 'tested'),
    ('FINISHED', 'finished'),
)

PRIORITY_CHOICES = (
    ('HIGH', 'high'),
    ('NORMAL', 'normal'),
    ('LOW', 'low'),
)


class Task(models.Model):

    creator = models.ForeignKey('auth.User', related_name='created_tasks', on_delete=models.CASCADE)

    target = models.ForeignKey(User, related_name='assigned_tasks', on_delete=models.CASCADE)

    title = models.CharField(max_length=100)

    description = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

    deadline = models.DateTimeField()

    priority = models.CharField(max_length=50, choices=PRIORITY_CHOICES, default='NORMAL')

    progress = models.CharField(max_length=50, choices=PROGRESS_CHOICES, default='ASSIGNED')

    is_finished = models.BooleanField(default=False)

    task_created = django.dispatch.Signal(providing_args=['creator', 'target',
                                                          'title', 'created',
                                                          'pk', 'is_finished'])

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/tasks/%i/" % self.pk

    #send notification, when task has been added/updated
    def send_notification(self, instance):
        task_created.send(sender=self.__class__, creator=instance.creator.pk,
                          target=instance.target, title=instance.title,
                          created=instance.created, pk=instance.pk,
                          is_finished=instance.is_finished)