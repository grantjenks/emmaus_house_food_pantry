from django import db

class Item(db.models.Model):
    name = db.models.CharField(max_length=256)
    code = db.models.CharField(blank=True, null=True, max_length=256)
    donor = db.models.CharField(blank=True, null=True, max_length=256)
    acquire_date = db.models.DateField(blank=True, null=True)
    release_date = db.models.DateField(blank=True, null=True)
    category = db.models.CharField(blank=True, max_length=256)
    subcategory = db.models.CharField(blank=True, max_length=256)

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    def jsonDate(self, date):
        if date is None: return None
        else: return date.strftime('%b {}, %Y').format(date.day)
    def toJSON(self):
        acquire_date = self.jsonDate(self.acquire_date)
        release_date = self.jsonDate(self.release_date)
        return dict(num=self.id, name=self.name, code=self.code,
                    donor=self.donor,
                    acquire_date=acquire_date,
                    release_date=release_date,
                    category=self.category, subcategory=self.subcategory)

class Label(db.models.Model):
    name = db.models.CharField(max_length=256)
    code = db.models.CharField(unique=True, max_length=256)
    category = db.models.CharField(blank=True, max_length=256)
    subcategory = db.models.CharField(blank=True, max_length=256)

    def merge(self, **kwargs):
        update = False
        name = kwargs.get('name', '')
        category = kwargs.get('category', '')
        subcategory = kwargs.get('subcategory', '')
        if name != '' and name != self.name:
            self.name = name
            update = True
        if category != '' and category != self.category:
            self.category = category
            update = True
        if subcategory != '' and subcategory != self.subcategory:
            self.subcategory = subcategory
            update = True
        if update: self.save()
        return update
    def __str__(self):
        return '{0} {1}'.format(self.code, self.name)
    def __repr__(self):
        return '{0} {1}'.format(self.code, self.name)

def update_label(code, field, value):
    if field not in ('name', 'category', 'subcategory'):
        raise ValueError

    label = Label.objects.get(code=code)

    attr_value = getattr(label, field)
    if attr_value == value: return False

    setattr(label, field, value)
    label.save()

    items = Item.objects.filter(code=code)
    update = False

    for item in items:
        attr_value = getattr(item, field)
        if attr_value != value:
            setattr(item, field, value)
            item.save()
            update = True

    return update

class Category(db.models.Model):
    name = db.models.CharField(max_length=256)
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    class Meta:
        ordering = ['name']
        verbose_name_plural = "categories"

class Subcategory(db.models.Model):
    name = db.models.CharField(max_length=256)
    category = db.models.ForeignKey(Category)
    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    class Meta:
        ordering = ['name']
        verbose_name_plural = "subcategories"

class BagCount(db.models.Model):
    category = db.models.ForeignKey(Category, unique=True)
    count = db.models.IntegerField()
    def __str__(self):
        return '{}: {}'.format(self.category, self.count)
    def __repr__(self):
        return '{}: {}'.format(self.category, self.count)
    class Meta:
        ordering = ['category']

class Setting(db.models.Model):
    key = db.models.CharField(max_length=64, unique=True)
    value = db.models.CharField(max_length=512, blank=True, null=True)
    def __str__(self):
        return '{}: {}'.format(self.key, self.value)
    def __repr__(self):
        return '{}: {}'.format(self.key, self.value)
    class Meta:
        ordering = ['key']
