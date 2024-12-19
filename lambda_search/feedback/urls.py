from django.urls import path

from feedback.views import FeedbackView

app_name = "feedback"

urlpatterns = [
    path("", FeedbackView.as_view(), name="feedback"),
]
