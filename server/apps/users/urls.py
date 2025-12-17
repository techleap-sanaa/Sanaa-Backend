from django.urls import path
from .views import *

urlpatterns = [
    path("webhooks/users", ClerkWebhook.as_view()),
]
