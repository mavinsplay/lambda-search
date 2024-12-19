from django.urls import path

import about.views

app_name = "about"

urlpatterns = [
    path("terms/", about.views.TermsView.as_view(), name="terms"),
]
