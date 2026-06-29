from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserSigninForm

def signup(request):
    print(request.method)

    if request.method == 'POST':
        form = UserSigninForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponse("Signup done")  
        else:
            print(form.errors)     
    else:
        form = UserSigninForm()
    return render(request, "registration/signup.html", {"form":form})
