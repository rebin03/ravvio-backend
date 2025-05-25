from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.FloatField(null=True, blank=True)
    category_obj = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name='Category')
    
    def __str__(self):
        return self.name


class ProductAttribute(models.Model):
    name = models.CharField(max_length=100, unique=True)    

    def __str__(self):
        return self.name
    

class ProductAttributeItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, verbose_name="Specification")
    value = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.attribute}: {self.value}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images')
    order = models.IntegerField(default=0)  # For controlling display order
    caption = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.product.name}"