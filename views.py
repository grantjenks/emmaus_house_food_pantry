from models import Item, Label

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage
from django.core.paginator import InvalidPage, PageNotAnInteger
from django.template import RequestContext
from django.shortcuts import render_to_response

from datetime import datetime
import json

def lookup_label(request):
    if request.method != 'GET':
        return HttpResponseBadRequest()

    code = request.GET.get('code')

    if code is None: return HttpResponseBadRequest()

    result = dict(name='', category='', subcategory='')

    try:
        label = Label.objects.get(code=code)
        result['name'] = label.name
        result['category'] = label.category
        result['subcategory'] = label.subcategory
    except Label.DoesNotExist:
        pass

    return HttpResponse(json.dumps(result))

def item_new(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    code = request.POST.get("code")
    name = request.POST.get("name")
    donor = request.POST.get("donor")
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

    if name == '':
        result = {'message': 'Please enter a name.'}
        return HttpResponseBadRequest(json.dumps(result))

    if acquire_date:
        acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()
    else:
        acquire_date = None

    item = Item.objects.create(code=code, name=name, donor=donor,
                               acquire_date=acquire_date,
                               release_date=None,
                               category=category, subcategory=subcategory)

    return HttpResponse(json.dumps(item.toJson()))

def item_release(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    code = request.POST.get("code", None)

    if code is None:
        return HttpResponseBadRequest()

    try:
        item = Item.objects.filter(code=code, release_date=None)[:1][0]
        today = datetime.now().date()
        item.release_date = today
        item.save()
        return HttpResponse(json.dumps(item.toJson()))
    except Exception as ex:
        print ex
        return HttpResponseBadRequest()

def item_update(request):
    if request.method != 'POST':
        return HttpResponseBadRequest()

    num = request.POST.get("num", None)
    field = request.POST.get("field", None)
    value = request.POST.get("value", None)

    if field not in ('name', 'code', 'donor', 'acquire_date',
                     'release_date', 'category', 'subcategory'):
        return HttpResponseBadRequest()

    if field == 'name' and value == '': return HttpResponseBadRequest()

    try:
        if field == 'acquire_date':
            value = datetime.strptime(value, '%b %d, %Y').date()

        # TODO: If the name, category or subcategory is modified and
        # code is not None then we need to update all references in the
        # database.
        # And we need to update the UI.

        num = int(num)
        item = Item.objects.get(pk=num)
        setattr(item, field, value)
        item.save()
        return HttpResponse(json.dumps(item.toJson()))
    except Exception as ex:
        return HttpResponseBadRequest()

def inventory(request, page=1):
    """List items from inventory."""

    items = Item.objects.filter(release_date=None)
    items_paginator = Paginator(items, 20)

    try:
        items_page = items_paginator.page(page)
    except (PageNotAnInteger, EmptyPage, InvalidPage):
        raise Http404

    return render_to_response('inventory.html', {'items_page':items_page},
                              context_instance=RequestContext(request))

def receiving(request):
    return render_to_response('receiving.html', {},
                              context_instance=RequestContext(request))

def distribution(request):
    return render_to_response('distribution.html', {},
                              context_instance=RequestContext(request))

def receipt(request):
    donor = request.GET.get('donor')
    acquire_date = request.GET.get('acquire_date')

    if donor is None or acquire_date is None:
        data = {'error': 'Please specify donor and date.'}
        return render_to_response('receipt.html', data,
                                  context_instance=RequestContext(request))

    acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()

    items = Item.objects.filter(donor=donor, acquire_date=acquire_date)

    # Group by code with quantity.

    return render_to_response('receipt.html', {'items':items},
                              context_instance=RequestContext(request))
