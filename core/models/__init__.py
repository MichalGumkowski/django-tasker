from .comment import *
from .mail import *
from .notification import *
from .task import *
from .team import *

from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
import datetime


#create proper notification, when task has been added/modified
@receiver(post_save, sender=Task)
def task_created(sender, instance, created, **kwargs):

    text = ""
    date = instance.created
    # url
    domain = Site.objects.get_current().domain
    obj = Task.objects.get(id=instance.pk)
    path = obj.get_absolute_url()
    url = 'http://{domain}{path}'.format(domain=domain, path=path)

    #if task has been created inform the target
    if created:
        #Notification
        target = instance.target

        text = instance.creator.username + " added a new task for you: <b>" + \
               instance.title + ".</b>"

        Notification.objects.create(target=target, text=text, date=date,
                                    link=url, seen=False)

    #if bool has been finished (task was completed) was checked
    #send that information to the task creator
    elif instance.is_finished:
        target = instance.creator

        text = instance.target.username + " has finished his task: <b>" + \
               instance.title + ".</b>"

        Notification.objects.create(target=target, text=text, date=date,
                                    link=url, seen=False)

        # Mail
        mail_text = "Hi " + target.username + "!\n" + text + \
                    "\nTo check it - click the link.\n\n" + url

        Mail.objects.create(target=target, title=text,
                            text=mail_text, sent=False)

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

    comments = instance.task.comments.all()
    receivers = {instance.task.target, instance.task.creator}
    for com in comments:
        receivers |= {com.creator}

    receivers.remove(instance.creator)

    date = instance.date
    text = instance.creator.username + " just added a comment to the task: " + \
    instance.task.title

    # url
    domain = Site.objects.get_current().domain
    obj = Task.objects.get(id=instance.task.pk)
    path = obj.get_absolute_url()
    url = 'http://{domain}{path}'.format(domain=domain, path=path)

    for target in receivers:
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
