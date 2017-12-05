from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models



class Mail(models.Model):
    target = models.ForeignKey(User)

    title = models.CharField(
        max_length=250,
    )

    text = models.TextField()

    sent = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.target.email:
            send_mail(self.title, self.text,
                      'testingdjango111@gmail.com', [self.target.email])
            self.sent = True

        super(Mail, self).save(*args, **kwargs)