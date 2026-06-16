from django.urls import include, path
from home import  views

app_name = 'Home'
urlpatterns = [
    path('',views.HomeView.as_view(),name='home'),
    path('device/<int:device_id>/info/', views.DeviceInfoView.as_view(), name='device-info'),
    path('device/<int:device_id>/blocked-apps/', views.BlockAppsView.as_view(), name='blocked-apps'),

]