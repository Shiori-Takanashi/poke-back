from django.db import models

class Endpoint(models.Model):
    id = models.IntegerField(primary_key=True)
    category = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=1024, blank=True)
    url = models.CharField(max_length=100)
    using = models.BooleanField(default=False)

    def __str__(self):
        return self.name
