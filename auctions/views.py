from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import NewListingForm, NewBidForm
from .models import User, Listing, Category


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=Listing.Status.ACTIVE),
        "title": "Active Listings",
        })

@login_required 
def closed_listings(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=Listing.Status.CLOSED).filter(author=request.user),
        "title": "My Closed Listings",
        })

@login_required 
def won_listings(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=Listing.Status.CLOSED).filter(winner=request.user),
        "title": "My Won Listings",
        })

@login_required 
def my_listings(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=Listing.Status.ACTIVE).filter(author=request.user),
        "title": "My Listings",
        })

def category(request, category):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.filter(status=Listing.Status.ACTIVE).filter(category=Category.objects.get(name=category)),
        "title": category,
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
            next_url = request.POST.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("index")
        else:
            return render(
                request,
                "auctions/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request, "auctions/register.html", {"message": "Passwords must match."}
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "auctions/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


def list_categories(request):
    return render(request, "auctions/categories.html", {"categories": Category.objects.all()})


@login_required
def watchlist(request):
    return render(request, "auctions/watchlist.html")


@login_required
def create(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            listing = form.save(
                commit=False
            )  # to manually add the author and then save
            listing.author = request.user
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = NewListingForm()

    return render(request, "auctions/create.html", {"form": form})


@login_required
def listing_detail(request, id):
    listing = get_object_or_404(Listing, id=id)

    if request.method == "POST":
        form = NewBidForm(request.POST, user=request.user, listing=listing)
        if form.is_valid():
            new_bid = form.save(commit=False)
            new_bid.bidder = request.user
            new_bid.listing = listing
            new_bid.save()
            messages.success(request, "Bid successful!")
            return HttpResponseRedirect(reverse("listing_detail", args=[id]))
    else:
        form = NewBidForm(user=request.user, listing=listing)

    return render(
        request,
        "auctions/detail.html",
        {
            "form": form,
            "listing": listing,
        },
    )

@login_required
def delete_listing(request, id):
    listing = get_object_or_404(Listing, id=id)

    if listing.author != request.user:
        return HttpResponseForbidden("Only the author of a listing can delete it.")
    
    if request.method == "POST":
        listing.delete()
        messages.info(request, "Listing was deleted!")
        return HttpResponseRedirect(reverse("index"))
    
@login_required
def close_listing(request, id):
    listing = get_object_or_404(Listing, id=id)

    if listing.author != request.user:
        return HttpResponseForbidden("Only the author of a listing can close it.")
    
    if request.method == "POST":
        listing.status = 1
        listing.winner = listing.highest_bidder
        listing.save()
        messages.info(request, "Listing was closed!")
        return HttpResponseRedirect(reverse("index"))