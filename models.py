from django import db

class Item(db.models.Model):
    name = db.models.CharField(max_length=256)
    code = db.models.CharField(blank=True, null=True, max_length=256)
    donor = db.models.CharField(blank=True, null=True, max_length=256)
    expire_year = db.models.IntegerField(blank=True, null=True)
    acquire_date = db.models.DateField(blank=True, null=True)
    release_date = db.models.DateField(blank=True, null=True)
    category = db.models.CharField(blank=True, max_length=256)
    subcategory = db.models.CharField(blank=True, max_length=256)

    def __str__(self):
        return self.name
    def __repr__(self):
        return self.name
    def jsonDate(self, date):
        return date if date is None else date.strftime('%b %d, %Y')
    def toJson(self):
        acquire_date = self.jsonDate(self.acquire_date)
        release_date = self.jsonDate(self.release_date)
        expire_year = self.expire_year or ''
        return dict(num=self.id, name=self.name, code=self.code,
                    donor=self.donor, expire_year=expire_year,
                    acquire_date=acquire_date,
                    release_date=release_date,
                    category=self.category, subcategory=self.subcategory)

    class Meta:
        app_label = 'food_pantry'

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

    class Meta:
        app_label = 'food_pantry'
