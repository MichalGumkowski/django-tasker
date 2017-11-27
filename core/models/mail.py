from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.sites.models import Site
from django.core.mail import send_mail
import django.dispatch
import datetime


class Mail(models.Model):
    target = models.ForeignKey(User)

    title = models.CharField(
        max_length=250,
        default="Tasker: ",
    )

    text = models.TextField()

    sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.target.email:
            send_mail(self.title, self.text,
                      'testingdjango111@gmail.com', [self.target.email])

        super(Mail, self).save(*args, **kwargs)