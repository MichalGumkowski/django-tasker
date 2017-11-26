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


class Mail(models.Model):
    target = models.ForeignKey(User)

    title = models.CharField(
        max_length=250,
        default="Tasker: ",
    )

    text = models.TextField()

    sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        send_mail(self.title, self.text,
                  'testingdjango111@gmail.com', ['tored11@gmail.com'])

        super(Mail, self).save(*args, **kwargs)


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

    def save(self, *args, **kwargs):
        mail_target = self.target
        mail_title = "Tasker: " + self.text
        mail_text = "Hi! </br><b>" + self.text + "</br></b>" + \
                    "You can check it out by clicking the link shown below.</br>" + \
                    self.link
        Mail.objects.create(target=mail_target, title=mail_title,
                            text=mail_text, sent=False)
        super(Notification, self).save(*args, **kwargs)


#create proper notification, when task has been added/modified
@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):

    date = instance.created
    # url
    domain = Site.objects.get_current().domain
    obj = Task.objects.get(id=instance.pk)
    path = obj.get_absolute_url()
    url = 'http://{domain}{path}'.format(domain=domain, path=path)

    #if task has been created inform the target
    if created:
        target = instance.target

        text = instance.creator.username + " added a new task for you: <b>" + \
               instance.title + "<\\b>"

        Notification.objects.create(target=target, text=text, date=date,
                                    link=url, seen=False)
    #if bool has been finished (task was completed) was checked
    #send that information to the task creator
    elif instance.is_finished:
        target = instance.creator

        text = instance.target.username + " has finished his task: <b>" + \
               instance.title + "<\\b>"

        Notification.objects.create(target=target, text=text, date=date,
                                    link=url, seen=False)
    #if task was updated in any other way inform both creator and target
    else:
        target_1 = instance.creator
        target_2 = instance.target

        text = "<b>" + instance.title + "<\\b> has been changed"

        Notification.objects.create(target=target_1, text=text, date=date,
                                    link=url, seen=False)
        Notification.objects.create(target=target_2, text=text, date=date,
                                    link=url, seen=False)


#if comment has been added to the task, inform the other party
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


#if someone has been added/removed from the team, inform all the parties from the team
#all the data is taken from the serializer!
def team_changed(instance, old_members, **kwargs):
    date = datetime.datetime.now()
    link = ""

    added_members = []
    removed_members = []

    members = instance.members.all()
    team_name = instance.name
    text_added = " has been added to your team <b>" + team_name + "</b>"
    text_removed = " has been removed from your team <b>" + team_name + "</b>"
    self_added = "You have been added do the team <b>" + team_name + "</b>"
    self_removed = "You have been removed from your team <b>" + team_name + "</b>"

    for member in old_members:
        if member not in members:
            removed_members.append(member.username)
            Notification.objects.create(target=member, text=self_removed,
                                        date=date, link=link, seen=False)

    for member in members:
        if member not in old_members:
            added_members.append(member.username)

    for member in members:
        for removed in removed_members:
            text = "<b>" + removed + "</b>" + text_removed
            Notification.objects.create(target=member, text=text, date=date,
                                        link=link, seen=False)
        for added in added_members:
            text = ""

            if member.username != added:
                text = "<b>" + added + "</b>" + text_added
            else:
                text = self_added

            Notification.objects.create(target=member, text=text, date=date,
                                        link=link, seen=False)



