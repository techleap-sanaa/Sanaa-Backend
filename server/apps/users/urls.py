from django.urls import path
from .views import *

urlpatterns = [
    path("api/users", ClerkWebhook.as_view()),
]
