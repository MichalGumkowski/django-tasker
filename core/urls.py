from django.conf.urls import url, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'tasks', views.TaskViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'notifications', views.NotificationViewSet)
router.register(r'teams', views.TeamViewSet)


urlpatterns = [
    url(r'^', include(router.urls))
]