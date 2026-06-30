from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserSigninForm, BuyerSignupForm, LoginForm
from .models import User
from django.contrib.auth import login, authenticate

def signup(request):
    print(request.method)

    if request.method == 'POST':
        form = UserSigninForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) 
            if user.role == User.Role.BUYER:
                return redirect("buyer_signup")
            elif user.role == User.Role.SELLER:
                return redirect("seller_signup")
        else:
            print(form.errors)     
    else:
        form = UserSigninForm()
    return render(request, "registration/signup.html", {"form":form})


def buyer_signup(request):
    user = request.user

    if request.method == "POST":
        form = BuyerSignupForm(request.POST, request.FILES)

        if form.is_valid():
            buyer = form.save(commit=False)
            buyer.user = user
            buyer.save()

            return redirect("login")

    else:
        form = BuyerSignupForm()

    return render(request, "registration/buyer_signup.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            identifier = form.cleaned_data["identifier"]
            password = form.cleaned_data["password"]

            user = None

            try:
                user_obj = User.objects.get(username=identifier)
                user = authenticate(
                    request,
                    username=user_obj.username,
                    password=password,
                )
            except User.DoesNotExist:
                try:
                    user_obj = User.objects.get(email=identifier)
                    user = authenticate(
                        request,
                        username=user_obj.username,
                        password=password,
                    )
                except User.DoesNotExist:
                    pass

            if user:
                login(request, user)
                return redirect("home")

            form.add_error(None, "Invalid username/email or password.")

    else:
        form = LoginForm()

    return render(request, "registration/login.html", {
        "form": form
    })