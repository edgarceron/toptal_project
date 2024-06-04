from djongo import models

class Location(models.Model):
    type = models.CharField(max_length=10, default="Point")
    coordinates = models.JSONField()

    class Meta:
        abstract = True

# Create your models here.
class apartments(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.EmbeddedField(model_container=Location)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    dateaded = models.DateTimeField()
