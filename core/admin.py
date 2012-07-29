from django.contrib import admin
from models import Item, Label, Category, Subcategory, BagCount, Setting

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

class BagCountAdmin(admin.ModelAdmin):
    pass
admin.site.register(BagCount, BagCountAdmin)

class SettingAdmin(admin.ModelAdmin):
    pass
admin.site.register(Setting, SettingAdmin)
