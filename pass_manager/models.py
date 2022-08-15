from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Password(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cliant')
    title = models.CharField(max_length=500, null=True, blank=True)
    username = models.CharField(max_length=500, null=False, blank=False)
    password = models.CharField(max_length=500, null=False, blank=False)
    icon = models.CharField(max_length=250, null=True, blank=True)
    last_update = models.DateField(auto_now=True)

    def __str__(self):
        return self.title