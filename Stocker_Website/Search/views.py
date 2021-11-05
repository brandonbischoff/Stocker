from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import login, logout, authenticate

from . forms import ChooseSource, RegistrationForm, LoginForm
from. models import TheStocks, WatchList
from Search.scripts import create_img


# Create your views here.


def home(request):

    form = ChooseSource()

    return render(request, 'Search/home.html', {'form': form})


def Registration(request):

    if request.method == "POST":
        # The post attribute of the request object has all the info of the form
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)

                return redirect('home_page')
            else:
                return "could not authenticate"

        else:
            return (render(request, 'Search/signup.html', {"form": form}))
    else:

        form = RegistrationForm()
        return(render(request, 'Search/signup.html', {"form": form}))


def Login(request):

    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home_page')
            else:
                pass  # does not exist?
        else:
            # need to let the input was invalid
            return render(request, 'Search/login.html', {'form': form})

    else:
        form = LoginForm()
        return render(request, 'Search/login.html', {'form': form})


def SignOut(request):

    if request.user.is_authenticated:
        logout(request)

        return redirect('home_page')
    else:
        return HttpResponse("not logged in")


def Dashboard(request):

    if request.method == "POST":
        form = ChooseSource(request.POST)
        if form.is_valid():
            source = form.cleaned_data['source']
            date = form.cleaned_data['date']

            stock_objects = TheStocks.objects.filter(
                source__exact=source).filter(
                purchase_date__exact=date)

            stock_info = list(map(create_img.create_stock, stock_objects))

            if request.user.is_authenticated:
                user = request.user
                user_stock_objects = TheStocks.objects.filter(watchlist__user=user)

                return render(request, "Search/dashboard.html", {"stock": stock_info,
                                                                 "user_stocks": user_stock_objects,
                                                                 "form": form})
            else:
                return render(request, "Search/dashboard.html", {"stock": stock_info,
                                                                 "form": form})


    else:
        form = ChooseSource()
        return render(request, 'Search/dashboard.html', {'form': form})


def Watchlist(request):
    form = ChooseSource()
    if request.method == "POST":
        if request.POST.get("stock_id_add"):
            stock_primarykey = request.POST.get("stock_id_add")
            stock = TheStocks.objects.get(pk=stock_primarykey)
            user = request.user
            instance = WatchList(stock=stock, user=user)
            if instance:
                instance.save()
            return redirect("dashboard_page")

        elif request.POST.get("stock_id_remove"):
            stock_primarykey = request.POST.get("stock_id_remove")
            stock = TheStocks.objects.get(pk= stock_primarykey)
            user = request.user
            WatchList.objects.filter(stock= stock, user= user).delete()
            return redirect('watchlist_page')

        else:
            pass

    else:
        if request.user.is_authenticated:
            user = request.user
            user_stock_objects = TheStocks.objects.filter(watchlist__user=user)
            stock_info = list(map(create_img.create_stock, user_stock_objects))

        return render(request, 'Search/watchlist.html', {"stock": stock_info, "form": form})
