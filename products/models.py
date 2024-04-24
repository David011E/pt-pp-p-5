from django.db import models

# Create your models here.
class Category(models.Model):
    class Meta:
        verbose_name_plural = 'Categories' # To remove the s in the name in admin view

    name = models.CharField(max_length=254)
    type = models.TextField(default=0)

    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField()

    def __str__(self):
        return self.name