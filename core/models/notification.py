from django.db import models
from django.contrib.auth.models import User
from core.models.mail import Mail


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
        mail_text = "Hi " + self.target.username + "!\n" + self.text + \
                    "\nTo check it - click the link.\n\n" + self.link
        Mail.objects.create(target=mail_target, title=mail_title,
                            text=mail_text, sent=False)

        super(Notification, self).save(*args, **kwargs)

        # Mail
