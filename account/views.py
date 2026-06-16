from django.shortcuts import render,redirect
from django.views import View
from .forms import UserRegisterForm,UserLoginForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import login,authenticate,logout

class RegisterView(View):

    TEMPLATE_NAME = 'register.html'
    form_class=UserRegisterForm
    def get(self,request):
        return  render(request,self.TEMPLATE_NAME)

    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user=User.objects.create_user(
                username=cd['username'],
                email=cd['email'],
                password=cd['password']
            )
            messages.add_message(request,200,'Your account created!','success')
            login(request,user)
            return redirect('Home:home')
        return  render(request, self.TEMPLATE_NAME,{'form':form})



class LoginView(View):
    TEMPLATE_NAME = 'login.html'
    form_class = UserLoginForm

    def get(self,request):
        return render(request,self.TEMPLATE_NAME)

    def post(self,request):
        form = self.form_class(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            username_email = cd['username_email']
            password = cd['password']
            try:
                if '@' in username_email:
                        user = User.objects.get(email=username_email)
                        username = user.username
                else:
                    username = username_email
            except User.DoesNotExist:
                    return render(request, self.TEMPLATE_NAME, {'error': 'user not found!'})
            user = authenticate(request,username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('Home:home')
            else:
                return render(request,self.TEMPLATE_NAME,{"error":"information wrong or user is not found!"})
        return render(request, self.TEMPLATE_NAME, {'form': form})


class LogoutView(View):
    def get(self,request):
        logout(request)
        return redirect('Home:home')