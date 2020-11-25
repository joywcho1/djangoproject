from django.db import models


# parsed_date = datetime.strptime(mydate, "%Y-%m-%d")
# new_date = parsed_date + timedelta(days=1)

class SeaFood(models.Model):
    sfd_yyyy = models.CharField(max_length=4, blank=True)
    sfd_mm = models.CharField(max_length=2, blank=True)
    sfd_dd = models.CharField(max_length=2, blank=True)
    sfd_species = models.CharField(max_length=50, blank=True)
    sfd_orign = models.CharField(max_length=50, blank=True)
    sfd_standard = models.CharField(max_length=30, blank=True)
    packing_uint = models.CharField(max_length=30, blank=True)
    quantity = models.FloatField(blank=True, null=True)
    highest = models.IntegerField(blank=True, null=True)
    lowest = models.IntegerField(blank=True, null=True)
    average = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'seafood'
# Create your models here.
