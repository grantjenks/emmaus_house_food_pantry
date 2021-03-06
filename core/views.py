from models import Item, Label, update_label, BagCount, Setting

from django.db.models import Count
from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.core.paginator import Paginator, EmptyPage
from django.core.paginator import InvalidPage, PageNotAnInteger
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404

from datetime import datetime
from collections import Counter, OrderedDict
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
        try:
            acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()
        except ValueError:
            return HttpResponseBadRequest(
                json.dumps({'error':'Failed to parse date.'}),
                content_type='application/javascript; charset=utf8')
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
        item = Item.objects.filter(code=code, release_date=None)
        if len(item) == 0:
            return HttpResponseBadRequest(
                json.dumps({'error':'Item not found in inventory.'}),
                content_type='application/javascript; charset=utf8')
        item = item[:1][0]
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
        try:
            value = datetime.strptime(value, '%b %d, %Y').date()
        except ValueError:
            return HttpResponseBadRequest(
                json.dumps({'error':'Failed to parse date.'}),
                content_type='application/javascript; charset=utf8')

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
        if field == 'category':
            update |= update_label(code, 'subcategory', '')
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

def dashboard(request):
    items = Item.objects.filter(release_date=None)

    categories = items.values_list('category').annotate(Count('id'))
    categories = categories.order_by('category')
    bagcounts = OrderedDict((bag.category.name, bag.count)
                            for bag in BagCount.objects.order_by('category'))
    bagsperweek = int(Setting.objects.get(key='count/bags/week').value)
    categories = [(category,
                   count,
                   count / bagcounts[category],
                   count / bagcounts[category] / bagsperweek)
                  for category, count in categories]

    subcategories = items.values('subcategory').annotate(Count('id'))
    subcategories = subcategories.order_by('subcategory')

    low_inventory = int(Setting.objects.get(key='count/low/inventory').value)
    watchlist = filter(lambda tup: tup[3] <= low_inventory, categories)
    watchlist.sort(key=lambda tup: tup[2])

    return render_to_response('core/dashboard.html',
                              {'categories':categories,
                               'subcategories':subcategories,
                               'bagcounts':bagcounts,
                               'bagsperweek':bagsperweek,
                               'watchlist':watchlist},
                              context_instance=RequestContext(request))

def inventory(request, page=1):
    """List items from inventory."""

    items = Item.objects.filter(release_date=None).order_by('-id')
    items_paginator = Paginator(items, 20)

    try:
        items_page = items_paginator.page(page)
    except (PageNotAnInteger, EmptyPage, InvalidPage):
        raise Http404

    return render_to_response('core/inventory.html', {'items_page':items_page},
                              context_instance=RequestContext(request))

def receiving(request):
    return render_to_response('core/receiving.html', {},
                              context_instance=RequestContext(request))

def distribution(request):
    return render_to_response('core/distribution.html', {},
                              context_instance=RequestContext(request))

def history(request):
    donor = request.GET.get('donor')
    try:
        year = int(request.GET.get('year'))
    except (ValueError, TypeError):
        year = None

    donations = Item.objects.values('donor', 'acquire_date')
    if donor is not None: donations = donations.filter(donor=donor)
    if year is not None: donations = donations.filter(acquire_date__year=year)
    donations = donations.annotate(Count('id'))
    donations = donations.order_by('-acquire_date')

    donors = set()
    years = set()

    for donation in donations:
        donors.add(donation['donor'])
        years.add(donation['acquire_date'].year)

    donors = sorted(donors)
    years = sorted(years)

    return render_to_response('core/history.html',
                              {'donations':donations,
                               'curr_donor':donor,
                               'curr_year':year,
                               'donors':donors,
                               'years':years},
                              context_instance=RequestContext(request))

def receipt(request):
    donor = request.GET.get('donor')
    acquire_date = request.GET.get('acquire_date')

    if donor is None or acquire_date is None:
        data = {'error': 'Please specify donor and date.'}
        return render_to_response('core/receipt.html', { 'action': 'steps' },
                                  context_instance=RequestContext(request))

    try:
        acquire_date = datetime.strptime(acquire_date, '%b %d, %Y').date()
    except ValueError:
        return render_to_response('core/receipt.html',
                                  {'action':'steps',
                                   'error':'Error: Failed to parse date.'},
                                  context_instance=RequestContext(request))

    items = Item.objects.filter(donor=donor, acquire_date=acquire_date)
    subcategories = items.values('subcategory').annotate(Count('id'))
    subcategories = subcategories.order_by('subcategory')
    total = sum(subcategory['id__count'] for subcategory in subcategories)

    # Group by code with quantity.

    result = dict(groups=subcategories, donor=donor,
                  acquire_date=acquire_date, total=total, action='display')

    return render_to_response('core/receipt.html', result,
                              context_instance=RequestContext(request))

def version(request):
    import settings
    return HttpResponse(settings.VERSION,
                        content_type='text/plain; charset=utf8')

def shutdown(request):
    def call_exit():
        import os
        import time
        time.sleep(1)
        os._exit(0)
    from threading import Thread
    thread = Thread(target=call_exit)
    thread.start()
    return HttpResponse('Terminating server process ...',
                        content_type='text/plain; charset=utf8')
