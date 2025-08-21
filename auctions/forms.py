from django import forms
from .models import Listing, Bid

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit


class NewListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ["title", "description", "image", "starting_bid", "category"]

        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 10,
                }
            )
        }


class NewBidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["price"]
        labels = {"price": ""}
        widgets = {"price": forms.NumberInput(attrs={"placeholder": "Enter your bid"})}

    def __init__(self, *args, user=None, listing=None, **kwargs) -> None:
        """Accept listing so we can validate against it."""
        self.user = user
        self.listing = listing
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("price", css_class="form-control"),
            Submit("submit", "Place Bid", css_class="btn btn-primary"),
        )
        self.helper.include_media = False

    def clean_price(self) -> float | forms.ValidationError:
        """Validate that price is higher than starting_bid and highest bid."""
        price = self.cleaned_data["price"]

        if not self.listing:
            raise forms.ValidationError("Listing is required for validation.")

        # Must be higher than starting bid
        if price <= self.listing.starting_bid:
            raise forms.ValidationError(
                f"Your bid must be higher than the starting bid (${self.listing.starting_bid})."
            )

        # Must also be higher than highest existing bid (if any)
        highest_bid = (
            Bid.objects.filter(listing=self.listing).order_by("-price").first()
        )
        if highest_bid and price <= highest_bid.price:
            raise forms.ValidationError(
                f"Your bid must be higher than the current highest bid (${highest_bid.price})."
            )

        return price

    def clean(self):
        cleaned_data = super().clean()
        if self.user == self.listing.author:
            self.add_error("price", "You cannot bid on your own listing.")
        return cleaned_data
