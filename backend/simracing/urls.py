from django.urls import path
from . import views

urlpatterns = [
    #this allows us to redirect api request to the correct function that can return data
    path('new-session/', views.newSession, name='new-session'), 
    path('get-track-car-driver/', views.getTrackCarDriver, name='get-track-car-driver'), 
    path('lap-list/', views.getLaps, name='lap-list'),
    path('prepare-race/', views.prepareRace, name='prepare-race'),
    path('get-sessions/', views.getSession, name='get-sessions'),
    path('update-lap/', views.updateLap, name='update-lap'),
    path('get-session-info/', views.getSessionInfo, name='get-lap-session'),
    path('get-session-stat/', views.getSessionStat, name='get-session-info'),
    path('get-lap-info/', views.getLapInfo, name='get-lap-info'),
    path('get-lap-telemetry/', views.getLapTelemetry, name='get-lap-telemetry'),
    path('get-estimation-lap/', views.getEstimationLap, name='get-estimation-lap'),
    path('do-inertial-mapping/', views.doInertialMapping, name='do-inertial-mapping'),
]