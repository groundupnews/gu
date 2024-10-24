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
    
    TRANSACTION_STATUS = [
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('pending', 'Pending')
    ]

    PAYMENT_TYPE = [
        ('one_time', 'One Time'),
        ('subscription', 'Subscription')
    ]

    PLATFORM_OPTIONS = [
        ('paypal', 'Paypal'),
        ('snapscan', 'Snapscan'),
        ('payfast', 'Payfast')
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    datetime_of_donation = models.DateTimeField(blank=True, null=True)
    currency_type = models.ForeignKey(Currency, on_delete=models.CASCADE)
    amount = models.FloatField(default=0)
    notified = models.BooleanField(default=False)
    section18a_issued = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=TRANSACTION_STATUS,
        null=True, blank=True
    )
    payment_type = models.CharField(
        max_length=20, choices=PAYMENT_TYPE,
        null=True, blank=True
    )
    platform = models.CharField(
        max_length=50, choices=PLATFORM_OPTIONS,
        null=True, blank=True
    )

    def __str__(self):
        return str(self.datetime_of_donation) + "\t" + str(self.donor)

    def get_absolute_url(self):
        return reverse('donation.page', args=[])


class Subscription(models.Model):

    SUBSCRIPTION_STATUS = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('cancelled', 'Cancelled')
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    subscription_id = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=SUBSCRIPTION_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    failed_payments = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.donor.email
