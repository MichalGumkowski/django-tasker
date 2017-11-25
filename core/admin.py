from django.contrib import admin
from .models import Task
from .models import Comment
from .models import Team
from .models import Notification

admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Team)
# Register your models here.
