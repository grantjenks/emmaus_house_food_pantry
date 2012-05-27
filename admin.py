from django.contrib import admin
from models import Item, Label

class ItemAdmin(admin.ModelAdmin):
    pass
admin.site.register(Item, ItemAdmin)

class LabelAdmin(admin.ModelAdmin):
    pass
admin.site.register(Label, LabelAdmin)
