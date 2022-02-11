from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from annoying.functions import get_object_or_None

from .models import User, Listing, Bid, Comment, Watchlist, Winner


def index(request):
    products = []
    allproducts = Listing.objects.all()
    empty = False

    if len(allproducts) == 0:
        empty = True
    
    else:
        for product in allproducts:
            if len(Winner.objects.filter(listingid=product.id)) == 0:
                products.append(Listing.objects.get(id=product.id))
        if len(products) == 0:
            empty = True

    return render(request, "auctions/index.html", {
        "products": products,
        "empty": empty
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



@login_required(login_url='/login')
def createlisting(request):

    if request.method == "POST":
        item = Listing()
        item.seller = request.user.username
        item.title = request.POST.get('title')
        item.description = request.POST.get('description')
        item.starting_bid = request.POST.get('starting_bid')
        item.category = request.POST.get('category')

        if request.POST.get('image_link'):
            item.image_link = request.POST.get('image_link')

        item.save()

        return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/createlisting.html")


def viewlisting(request, product_id):
    comments = Comment.objects.filter(listingid=product_id)
    winners = Winner.objects.filter(listingid=product_id)

    closed = False
    winner = None
    if len(winners) != 0:
        winner = Winner.objects.get(listingid=product_id)
        closed = True

    if request.method == "POST":
        item = Listing.objects.get(id=product_id)
        newbid = int(request.POST.get('newbid'))

        if item.starting_bid >= newbid:
            product = Listing.objects.get(id=product_id)
            return render(request, "auctions/viewlisting.html", {
                "product": product,
                "message": "Your Bid should be higher than the Current one.",
                "msg_type": "danger",
                "comments": comments,
                "closed": closed,
                "winner": winner
            })

        else:
            item.starting_bid = newbid
            item.save()

            bidobj = Bid.objects.filter(listingid=product_id)
            if bidobj:
                bidobj.delete()
            obj = Bid()
            obj.user = request.user.username
            obj.title = item.title
            obj.listingid = product_id
            obj.bid = newbid
            obj.save()
            product = Listing.objects.get(id=product_id)
            return render(request, "auctions/viewlisting.html", {
                "product": product,
                "message": "Bid successful",
                "msg_type": "success",
                "comments": comments,
                "closed": closed,
                "winner": winner
            })

    else:
        product = Listing.objects.get(id=product_id)
        added = Watchlist.objects.filter(listingid=product_id, user=request.user.username)
        return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments,
            "closed": closed,
            "winner": winner
        })


@login_required(login_url='/login')
def addtowatchlist(request, product_id):
    obj = Watchlist.objects.filter(
        listingid=product_id, user=request.user.username)
    comments = Comment.objects.filter(listingid=product_id)

    if obj:
        obj.delete()
        product = Listing.objects.get(id=product_id)
        added = Watchlist.objects.filter(listingid=product_id, user=request.user.username)
        return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments
        })

    else:
        obj = Watchlist()
        obj.user = request.user.username
        obj.listingid = product_id
        obj.save()

        product = Listing.objects.get(id=product_id)
        added = Watchlist.objects.filter(
            listingid=product_id, user=request.user.username)
        return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments
        })


@login_required(login_url='/login')
def addcomment(request, product_id):
    obj = Comment()
    obj.comment = request.POST.get("comment")
    obj.user = request.user.username
    obj.listingid = product_id
    obj.save()

    comments = Comment.objects.filter(listingid=product_id)
    product = Listing.objects.get(id=product_id)
    added = Watchlist.objects.filter(
        listingid=product_id, user=request.user.username)
    return render(request, "auctions/viewlisting.html", {
        "product": product,
        "added": added,
        "comments": comments
    })



@login_required(login_url='/login')
def closebid(request, product_id):

    winobj = Winner()
    product = Listing.objects.get(id=product_id)
    bidobj = Bid.objects.get(listingid=product_id)
    winobj.owner = request.user.username
    winobj.winner = bidobj.user
    winobj.listingid = product_id
    winobj.winprice = bidobj.bid
    winobj.title = bidobj.title
    winobj.save()

    winner = Winner.objects.get(listingid=product_id)

    closed = False
    if winner:
        closed = True

    product = Listing.objects.get(id=product_id)
    added = Watchlist.objects.filter(listingid=product_id, user=request.user.username)
    comments = Comment.objects.filter(listingid=product_id)
    
    return render(request, "auctions/viewlisting.html", {
            "product": product,
            "added": added,
            "comments": comments,
            "closed": closed,
            "winner": winobj
        })
    
    
def categories(request):
    return render(request, "auctions/categories.html")


def category(request, category):
    category_products = []
    all_category_products = Listing.objects.filter(category=category)
    empty = False

    if len(all_category_products) != 0:
        for product in all_category_products:
            if len(Winner.objects.filter(listingid=product.id)) == 0:
                category_products.append(Listing.objects.get(id=product.id))

    if len(category_products) == 0:
        empty = True
        
    return render(request, "auctions/category.html", {
        "category": category,
        "empty": empty,
        "products": category_products
    })


@login_required(login_url='/login')
def watchlist(request):
    lst = Watchlist.objects.filter(user=request.user.username)
    present = False
    watchlst = []
    if lst:
        present = True
        for item in lst:
            product = Listing.objects.get(id=item.listingid)
            watchlst.append(product)
    return render(request, "auctions/watchlist.html", {
        "present": present,
        "product_list": watchlst
    })