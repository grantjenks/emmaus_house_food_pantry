from models import Item, Label

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage
from django.core.paginator import InvalidPage, PageNotAnInteger
from django.template import RequestContext
from django.shortcuts import render_to_response

from datetime import datetime
import json

def item_new(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    code = request.POST.get("code")
    name = request.POST.get("name")
    donor = request.POST.get("donor")
    expire_year = request.POST.get("expire_year")
    acquire_date = request.POST.get("acquire_date")
    category = request.POST.get("category")
    subcategory = request.POST.get("subcategory")

    if code != '':
        try:
            label = Label.objects.get(code=code)
            update = label.merge(name=name, category=category,
                                 subcategory=subcategory)
            name = label.name
            category = label.category
            subcategory = label.subcategory
        except Label.DoesNotExist:
            if name == '': return HttpResponseBadRequest()
            Label.objects.create(name=name, code=code, category=category,
                                 subcategory=subcategory)

    if name == '': return HttpResponseBadRequest()

    if expire_year == '':
        expire_year = None
    else:
        expire_year = int(expire_year)
        
    if acquire_date:
        acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()
    else:
        acquire_date = None

    item = Item.objects.create(code=code, name=name, donor=donor,
                               expire_year=expire_year,
                               acquire_date=acquire_date,
                               release_date=None,
                               category=category, subcategory=subcategory)

    return HttpResponse(json.dumps(item.toJson()))

def item_update(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    num = request.POST.get("num", None)
    field = request.POST.get("field", None)
    value = request.POST.get("value", None)

    if field not in ('name', 'code', 'donor', 'expire_year', 'acquire_date',
                     'category', 'subcategory'):
        return HttpResponseBadRequest()

    if field == 'name' and value == '': return HttpResponseBadRequest()

    try:
        if field == 'expire_year':
            value = int(value)
        elif field == 'acquire_date':
            value = datetime.strptime(value, '%b %d, %Y').date()

        # TODO: If the name, category or subcategory is modified and
        # code is not None then we need to update all references in the
        # database.
        # And we need to update the UI.

        num = int(num)
        item = Item.objects.get(pk=num)
        setattr(item, field, value)
        item.save()
        return HttpResponse()
    except Exception as ex:
        print ex
        return HttpResponseBadRequest()

def inventory(request, page=1):
    """List items from inventory."""

    all_items = Item.objects.all()
    items_paginator = Paginator(all_items, 20)

    try:
        items_page = items_paginator.page(page)
    except (PageNotAnInteger, EmptyPage, InvalidPage):
        raise Http404

    return render_to_response('inventory.html', {'items_page':items_page},
                              context_instance=RequestContext(request))

def receive(request):
    return render_to_response('receive.html', {},
                              context_instance=RequestContext(request))

def distribute(request):
    return render_to_response('dispense.html', {},
                              context_instance=RequestContext(request))
