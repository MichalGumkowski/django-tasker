from django.db import models
from django.contrib.auth.models import User

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

    def __str__(self):
        return self.title


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

    def __str__(self):
        return self.creator.username + '\'s comment to ' + \
                    self.task.title + ' task'




