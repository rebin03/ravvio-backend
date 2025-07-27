from django.contrib import admin
from django import forms
from django.urls import reverse
from django.utils.html import format_html
from .models import Category, Product, ProductAttribute, ProductAttributeItem, ProductImage

# Change admin site title
admin.site.site_header = "Ravvio Admin"
admin.site.site_title = "Ravvio Admin Portal"
admin.site.index_title = "Welcome to Ravvio Admin Portal"

# Inline for product attributes
class ProductAttributeItemInline(admin.TabularInline):
    model = ProductAttributeItem
    extra = 1
    autocomplete_fields = ['attribute']

# Inline for product images
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    max_num = 4  # Limit to a maximum of 4 images per product
    verbose_name = "Product Image"
    verbose_name_plural = "Product Images (Maximum 4)"

# Custom form for Product with category autocomplete
class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'category_obj': forms.Select(attrs={'class': 'select2'}),
        }

# Category admin with search
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']

# ProductAttribute admin with search
@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name']

# Main Product admin
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    inlines = [ProductAttributeItemInline, ProductImageInline]
    list_display = ['name', 'price', 'category_obj', 'view_attributes']
    list_filter = ['category_obj']
    search_fields = ['name', 'description']
    autocomplete_fields = ['category_obj']
    
    def view_attributes(self, obj):
        count = obj.attributes.count()
        if count:
            url = reverse('admin:product_productattributeitem_changelist') + f'?product__id__exact={obj.id}'
            return format_html('<a href="{}">View {} Attributes</a>', url, count)
        return "No attributes"
    
    view_attributes.short_description = "Attributes"
    
    class Media:
        css = {
            'all': ('admin/css/autocomplete.css',)
        }
        js = ('admin/js/autocomplete.js',)

# Register ProductAttributeItem separately for direct access if needed
@admin.register(ProductAttributeItem)
class ProductAttributeItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'attribute', 'value']
    list_filter = ['product', 'attribute']
    search_fields = ['product__name', 'attribute__name', 'value']
    autocomplete_fields = ['product', 'attribute']

# Register ProductImage separately for direct access if needed
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image', 'order', 'caption']
    list_filter = ['product']
    search_fields = ['product__name', 'caption']
    autocomplete_fields = ['product']
