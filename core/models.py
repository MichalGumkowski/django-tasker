from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.urls import reverse
import django.dispatch

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

    def send_notification(self, instance):
        task_created.send(sender=self.__class__, creator=instance.creator.pk,
                          target=instance.target, title=instance.title,
                          created=instance.created, pk=instance.pk,
                          is_finished=instance.is_finished)


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

    def send_notification(self, instance):
        task_created.send(sender=self.__class__, creator=instance.creator.pk,
                          date=instance.date, pk=instance.pk)


class Notification(models.Model):

    target = models.ForeignKey(
        User,
        related_name='notification',
        blank=False,
        null=False
    )

    text = models.CharField(
        max_length=200,
        null=False,
        blank=False
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    link = models.TextField(
        blank=True
    )

    seen = models.BooleanField(
        default=False
    )


@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):

    date = instance.created
    # url
    domain = Site.objects.get_current().domain
    obj = Task.objects.get(id=instance.pk)
    path = obj.get_absolute_url()
    url = 'http://{domain}{path}'.format(domain=domain, path=path)

    if created:
        target = instance.target

        text = instance.creator.username + " added a new task for you: <b>" + \
               instance.title + "<\\b>"

        Notification.objects.create(target=target, text=text, date=date,
                                    link=url, seen=False)
    elif instance.is_finished:
        target = instance.creator

        text = instance.target.username + " has finished his task: <b>" + \
               instance.title + "<\\b>"

        Notification.objects.create(target=target, text=text, date=date,
                                    link=url, seen=False)
    else:
        target_1 = instance.creator
        target_2 = instance.target

        text = "<b>" + instance.title + "<\\b> has been changed"

        Notification.objects.create(target=target_1, text=text, date=date,
                                    link=url, seen=False)
        Notification.objects.create(target=target_2, text=text, date=date,
                                    link=url, seen=False)



@receiver(post_save, sender=Comment)
def comment_created(sender, instance, **kwargs):

    target = ""
    date = instance.date
    text = instance.creator.username + " just added a comment to the task: " + \
    instance.task.title

    # url
    domain = Site.objects.get_current().domain
    obj = Task.objects.get(id=instance.task.pk)
    path = obj.get_absolute_url()
    url = 'http://{domain}{path}'.format(domain=domain, path=path)

    if instance.task.creator == instance.creator:
        target = instance.task.target
    else:
        target = instance.task.creator

    Notification.objects.create(target=target, text=text, date=date,
                                link=url, seen=False)




