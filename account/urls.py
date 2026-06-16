from django.urls import path,include
from account import views

app_name = 'Account'
urlpatterns = [
    path('register/',views.RegisterView.as_view(),name='Register'),
    path('login/', views.LoginView.as_view(), name='Login'),
    path('logiur/',views.LogoutView.as_view(),name='Logout')

]