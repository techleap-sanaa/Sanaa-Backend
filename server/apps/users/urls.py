from django.urls import path
from .views import *

urlpatterns = [
    path("webhook/users", ClerkWebhook.as_view()),
]
