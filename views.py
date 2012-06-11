from models import Item, Label, update_label

from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage
from django.core.paginator import InvalidPage, PageNotAnInteger
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from datetime import datetime
from collections import Counter
import json

def lookup_label(request):
    if request.method != 'GET':
        return HttpResponseBadRequest(
            json.dumps({'error':'Only GET method supported.'}),
            content_type='application/javascript; charset=utf8')

    code = request.GET.get('code')

    if code is None:
        return HttpResponseBadRequest(
            json.dumps({'error':'Missing request parameter: code'}),
            content_type='application/javascript; charset=utf8')

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
        return HttpResponseBadRequest(
            json.dumps({'error':'Only POST method supported.'}),
            content_type='application/javascript; charset=utf8')

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
            if name == '':
                return HttpResponseBadRequest(
                    json.dumps({'error':'Name is a required field.'}),
                    content_type='application/javascript; charset=utf8')
            Label.objects.create(name=name, code=code, category=category,
                                 subcategory=subcategory)

    if name == '':
        return HttpResponseBadRequest(
            json.dumps({'error':'Name is a required field.'}),
            content_type='application/javascript; charset=utf8')

    if acquire_date:
        acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()
    else:
        acquire_date = None

    item = Item.objects.create(code=code, name=name, donor=donor,
                               acquire_date=acquire_date,
                               release_date=None,
                               category=category, subcategory=subcategory)

    return HttpResponse(json.dumps(item.toJSON()))

def item_release(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(
            json.dumps({'error':'Only POST method supported.'}),
            content_type='application/javascript; charset=utf8')

    code = request.POST.get("code", None)

    if code is None:
        return HttpResponseBadRequest(
            json.dumps({'error':'Missing request parameter: code'}),
            content_type='application/javascript; charset=utf8')

    try:
        item = Item.objects.filter(code=code, release_date=None)[:1][0]
        today = datetime.now().date()
        item.release_date = today
        item.save()
        return HttpResponse(json.dumps(item.toJSON()))
    except Exception as ex:
        return HttpResponseBadRequest(
            json.dumps({'error':str(ex)}),
            content_type='application/javascript; charset=utf8')

def item_update(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(
            json.dumps({'error':'Only POST method supported.'}),
            content_type='application/javascript; charset=utf8')

    num = request.POST.get("num", None)
    field = request.POST.get("field", None)
    value = request.POST.get("value", None)

    if field not in ('name', 'code', 'donor', 'acquire_date', 'release_date',
                     'release_date', 'category', 'subcategory'):
        return HttpResponseBadRequest(
            json.dumps({'error':'Field not recognized.'}),
            content_type='application/javascript; charset=utf8')

    if field == 'name' and value == '':
        return HttpResponseBadRequest(
            json.dumps({'error':'Name is a required field.'}),
            content_type='application/javascript; charset=utf8')

    if field in ('acquire_date', 'release_date'):
        value = datetime.strptime(value, '%b %d, %Y').date()

    num = int(num)
    item = get_object_or_404(Item, pk=num)
    setattr(item, field, value)

    if field == 'code':
        try:
            label = Label.objects.get(code=value)
            item.name = label.name
            item.category = label.category
            item.subcategory = label.subcategory
        except Label.DoesNotExist:
            Label.objects.create(name=item.name, code=value,
                                 category=item.category,
                                 subcategory=item.subcategory)

    item.save()

    code = item.code
    if code is not None and field in ('name', 'category', 'subcategory'):
        update = update_label(code, field, value)
    else:
        update = False

    result = dict(update=update, item=item.toJSON())

    return HttpResponse(json.dumps(result))

def item_delete(request):
    if request.method != 'POST':
        return HttpResponseBadRequest(
            json.dumps({'error':'Only POST method supported.'}),
            content_type='application/javascript; charset=utf8')

    num = request.POST.get("num", None)
    num = int(num)

    try:
        item = Item.objects.get(pk=num)
    except Item.DoesNotExist:
        return HttpResponseBadRequest(
            json.dumps({'error':'Item not found.'}),
            content_type='application/javascript; charset=utf8')

    item.delete()

    return HttpResponse()

def inventory(request, page=1):
    """List items from inventory."""

    items = Item.objects.filter(release_date=None).order_by('-id')
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
        return render_to_response('receipt.html', { 'action': 'steps' },
                                  context_instance=RequestContext(request))

    acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()

    items = Item.objects.filter(donor=donor, acquire_date=acquire_date)
    subcategories = items.values_list('subcategory', flat=True)
    total = len(subcategories)
    subcategories = dict(Counter(subcategories))

    # Group by code with quantity.

    result = dict(subcategories=subcategories, donor=donor,
                  acquire_date=acquire_date, total=total, action='display')

    return render_to_response('receipt.html', result,
                              context_instance=RequestContext(request))
