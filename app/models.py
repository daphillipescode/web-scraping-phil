from django.db import models


class UrlsProcess(models.Model):
    url = models.CharField(max_length=255)
    scrape = models.BooleanField(default=False)
    date_scrape = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'app_urls_process'


class UnprocessUrls(models.Model):
    url = models.CharField(max_length=255)
    scrape = models.BooleanField(default=False)
    date_scrape = models.DateTimeField(auto_now_add=False, null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'app_urls_unprocess'


class Results(models.Model):
    url = models.ForeignKey('UrlsProcess', models.RESTRICT)
    title = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.TextField(null=True, blank=True)
    beds = models.TextField(null=True, blank=True)
    baths = models.TextField(null=True, blank=True)
    sqft = models.TextField(null=True, blank=True)
    property_type = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    sub_type = models.TextField(null=True, blank=True)
    style = models.TextField(null=True, blank=True)
    lot_size = models.TextField(null=True, blank=True)
    lot_info = models.TextField(null=True, blank=True)
    mls_number = models.TextField(null=True, blank=True)
    parking_info = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    association_fee = models.TextField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'app_results'


class ResultsImages(models.Model):
    result = models.ForeignKey('Results', models.DO_NOTHING)
    image = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'app_results_images'