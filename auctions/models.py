from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Listing(models.Model):
    class Status(models.IntegerChoices):
        ACTIVE = 0, "Active"
        CLOSED = 1, "Closed"

    title = models.CharField(max_length=128)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings_authored")
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="listing_images", blank=True, null=True)
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, blank=True, null=True
    )
    date_posted = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    winner = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="listings_won")

    def __str__(self):
        return self.title

    @property
    def highest_bid(self) -> int:
        return self.bids.order_by("-price").first()

    @property
    def highest_bidder(self) -> User:
        return self.bids.order_by("-price").first().bidder
    
    @property
    def bid_count(self) -> int:
        return self.bids.count()

    def is_highest_bidder(self, user) -> bool:
        return self.highest_bid is not None and self.highest_bid.bidder == user
    
class Comment(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
            Listing, on_delete=models.CASCADE, related_name="comments", null=True
        )

class Bid(models.Model):
    price = models.FloatField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="bids", null=True
    )

    def __str__(self):
        return f"#{self.id}: ${self.price} for '{self.listing}' by {self.bidder}"


class Watchlist(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
