from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create, name="create"),
    path("item/<int:item_id>", views.item, name="item"),
    path("bidprocess", views.bidprocess, name="bidprocess"),
    path("error/<int:item_id>", views.error, name="error"),
    path("success/<int:item_id>", views.success, name="success"),
    path("closebidding", views.closebidding, name="closebidding"),
    path("closedlistings", views.closedlistings, name="closedlistings"),
    path("watchlistitems", views.watchlistitems, name="watchlistitems"),
    path("userposts", views.userposts, name="userposts"),
    path("itemcountbycategory", views.itemcountbycategory, name="itemcountbycategory"),
    path("itemlistbycategory/<int:category_id>", views.itemlistbycategory, name="itemlistbycategory"),
    path("commentprocess", views.commentprocess, name="commentprocess")
]
