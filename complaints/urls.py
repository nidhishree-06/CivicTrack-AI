
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('report/', views.report_complaint, name='report'),

    path(
        'success/<uuid:tracking_id>/',
        views.complaint_success,
        name='complaint_success'
    ),

    path(
        'dashboard/',
        views.authority_dashboard,
        name='authority_dashboard'
    ),

    path(
        'track/',
        views.track_complaint,
        name='track_complaint'
    ),
]
