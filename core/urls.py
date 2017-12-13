from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'mails', views.MailViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]

