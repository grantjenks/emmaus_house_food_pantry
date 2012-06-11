from django.contrib import admin
from models import Item, Label, Category, Subcategory

class ItemAdmin(admin.ModelAdmin):
    pass
admin.site.register(Item, ItemAdmin)

class LabelAdmin(admin.ModelAdmin):
    pass
admin.site.register(Label, LabelAdmin)

class CategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Category, CategoryAdmin)

class SubcategoryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Subcategory, SubcategoryAdmin)
