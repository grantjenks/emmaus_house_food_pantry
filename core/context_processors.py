
from models import Category, Subcategory

def categories(request):
    categories = Category.objects.all()

    subcategories = {}
    for cat in categories:
        subcategories[cat.name] = cat.subcategory_set.all()

    return {'categories':categories, 'subcategories':subcategories}
