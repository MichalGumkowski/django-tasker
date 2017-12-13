import django.dispatch
from .task import *


class Comment(models.Model):

    creator = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='comments',
    )

    date = models.DateTimeField(
        auto_now_add=True
    )

    text = models.TextField(default="")

    comment_added = django.dispatch.Signal(providing_args=['creator', 'task',
                                                           'date', 'pk', 'task'])

    def __str__(self):
        return self.creator.username + '\'s comment to ' + \
                    self.task.title + ' task'

    #send notification when comment has been added
    def send_notification(self, instance):
        comment_created.send(sender=self.__class__, creator=instance.creator,
                             date=instance.date, pk=instance.pk,
                             task=instance.task)