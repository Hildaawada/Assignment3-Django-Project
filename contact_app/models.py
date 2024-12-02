from django.db import models

# Create your models here.


class Professional(models.Model):
    EXPERTISE_CHOICES = [
        ('JR', 'Junior'),
        ('SR', 'Senior'),
        ('EX', 'Expert'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    state = models.CharField(max_length=100)
    expertise = models.CharField(max_length=2, choices=EXPERTISE_CHOICES, default='JR')
    service_cost_per_hour = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"