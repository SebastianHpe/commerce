from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("closed/", views.closed_listings, name="closed_listings"),
    path("won/", views.won_listings, name="won_listings"),
    path("my-listings/", views.my_listings, name="my_listings"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("categories/", views.list_categories, name="list_categories"),
    path("category/<str:category>/", views.category, name="category"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("create/", views.create, name="create"),
    path("listing/<int:id>/", views.listing_detail, name="listing_detail"),
    path('listing/<int:id>/delete/', views.delete_listing, name="delete_listing"),
    path('listing/<int:id>/close/', views.close_listing, name="close_listing"),
]
