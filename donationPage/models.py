from django.db import models
from django.urls import reverse

# Create your models here.
#donor as a class let's us track the number of donations a given donor has made and highlight top donors as needed.
#this also let's us collect multiple donations together so lists won't be filled with a single donor
class Donor(models.Model):
    name=models.CharField(max_length=200)
    display_name=models.CharField(max_length=200, blank=True)
    email=models.CharField(max_length=200)
    donor_url=models.CharField(max_length=50, blank=True, unique=True) #last 14 digits are a datetime for donor creation, remaining 36 digits are randomly generated
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse('donation.dashboard', args=[self.donor_url, ])

class Currency(models.Model):
    currency_abr=models.CharField(max_length=5, unique=True)
    def __str__(self):
        return self.currency_abr

#the Donation class has to handle the individual donations and connect them to donor regardless of time and platform
class Donation(models.Model):
    
    donor=models.ForeignKey(Donor, on_delete=models.CASCADE)
    datetime_of_donation=models.DateTimeField(blank=True, null=True)
    currency_type=models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount=models.FloatField(default=0)
    notified=models.BooleanField(default=False)
    section18a_issued=models.BooleanField(default=False)
    #platform=models.CharField(max_length=200)
    #certificate_issued=models.CharField(max_length=200)
    def __str__(self):
        return str(self.datetime_of_donation) + "\t" + str(self.donor)
    def get_absolute_url(self):
        return reverse('donation.page', args=[])
