from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Category, Comment, Item, Bid


def combineItemPrice(items):
    prices = [item.bid.price if hasattr(item, 'bid') else None for item in items]
    return zip(items, prices)

def index(request):
    items = Item.objects.all().filter(open=True)
    
    return render(request, "auctions/index.html", {
        "contents":combineItemPrice(items),
        "page_heading" : "Active Listings"
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required(login_url='login')
def create(request):
    if request.method == "POST":
        title = request.POST['title']
        description = request.POST['description']
        image_url = request.POST['image_url']
        if request.POST['category_id'] == "":
            category_id = 1
        else:
            category_id = int(request.POST['category_id'])
        starting_price = float(request.POST['starting_price'])
        print(starting_price)
        category = Category.objects.get(pk=category_id)
        item = Item(title = title, description=description, image_url=image_url, category=category, owner=request.user, open=True, starting_price=starting_price)
        item.save()
        return HttpResponseRedirect(reverse("item",args=[item.id]))

    categories = Category.objects.all()
    return render(request, "auctions/create.html", {
        "categories":categories
    })


def item(request, item_id):
    if request.method == "POST":
        item = Item.objects.get(pk=item_id)
        watchlist_flag = request.POST['watchlist_flag']
        if watchlist_flag == 'add':
            request.user.watchlist.add(item)
        else:
            request.user.watchlist.remove(item)
        return HttpResponseRedirect(reverse("item", args=[item_id]))

    item = Item.objects.get(pk=item_id)
    if hasattr(item, 'bid'):
        bid = item.bid
    else:
        bid = None

    if not request.user.is_authenticated:
        watchlist_flag = None
    elif item in request.user.watchlist.all():
        watchlist_flag = "remove"
    else:
        watchlist_flag = "add"

    comments = item.comments.all()

    return render(request, "auctions/item.html", {
        "item":item,
        "bid":bid,
        "watchlist_flag":watchlist_flag,
        "comments":comments
    })


@login_required(login_url='login')
def bidprocess(request):
    if request.method == "POST":
        item_id = int(request.POST['item_id'])
        bidding_price = float(request.POST['new_bid'])
        item = Item.objects.get(pk=item_id)
        if bidding_price > item.starting_price:
            if hasattr(item, 'bid'):
                if bidding_price > item.bid.price:
                    Bid.objects.filter(item=item).update(price=bidding_price)
                    Bid.objects.filter(item=item).update(bidder=request.user)
                    return HttpResponseRedirect(reverse("success", args=[item_id]))
                else:
                    return HttpResponseRedirect(reverse("error", args=[item_id]))
            else:
                bid = Bid(item=item, bidder=request.user, price=bidding_price)
                bid.save()
                return HttpResponseRedirect(reverse("success", args=[item_id]))
        else:
            return HttpResponseRedirect(reverse("error", args=[item_id]))


@login_required(login_url='login')
def error(request, item_id):
    return render(request, "auctions/error.html", {
        'item_id' : item_id
    })


@login_required(login_url='login')
def success(request, item_id):
    return render(request, "auctions/success.html", {
        'item_id' : item_id
    })


@login_required(login_url='login')
def closebidding(request):
    if request.method == "POST":
        item_id= int(request.POST['item_id'])
        Item.objects.filter(id=item_id).update(open=False)
        return HttpResponseRedirect(reverse("item", args=[item_id]))


def closedlistings(request):
    items = Item.objects.all().filter(open=False)
    return render(request, "auctions/index.html", {
        "contents":combineItemPrice(items),
        "page_heading":"Closed Listings"
    })


@login_required(login_url='login')
def watchlistitems(request):
    items = request.user.watchlist.all()
    return render(request, "auctions/index.html", {
        "contents":combineItemPrice(items),
        "page_heading":f"Watchlist of {request.user.username}"
    })


@login_required(login_url='login')
def userposts(request):
    items = request.user.items.all()
    return render(request, "auctions/index.html", {
        "contents":combineItemPrice(items),
        "page_heading":f"Items Posted by {request.user.username}"
    })


def itemcountbycategory(request):
    categories = Category.objects.all()
    counts = [len(category.items.all()) for category in categories]
    return render(request, "auctions/itemcountbycategory.html", {
        "contents":zip(categories, counts)
    })


def itemlistbycategory(request, category_id):
    category = Category.objects.get(pk=category_id)
    items = category.items.all()
    return render(request, "auctions/index.html", {
        "contents":combineItemPrice(items),
        "page_heading":f"Items Under Category {category.title}"
    })


@login_required(login_url='login')
def commentprocess(request):
    if request.method == "POST":
        item_id = int(request.POST['item_id'])
        item = Item.objects.get(pk=item_id)
        owner = request.user
        text = request.POST["comment-text"]
        comment = Comment(item=item, owner=owner, text=text)
        comment.save()
        return HttpResponseRedirect(reverse("item",args=[item_id]))
