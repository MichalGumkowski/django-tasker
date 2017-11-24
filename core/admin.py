from django.contrib import admin
from .models import Task, Comment, Notification, Team

admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Team)
# Register your models here.
