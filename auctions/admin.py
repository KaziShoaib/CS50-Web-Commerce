from django.contrib import admin
from .models import User, Category, Item, Bid, Comment

class CategoryAdmin(admin.ModelAdmin):
  list_display = ("id","title")

# Register your models here.
admin.site.register(User)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Item)
admin.site.register(Comment)
admin.site.register(Bid)