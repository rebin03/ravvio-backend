from rest_framework import serializers
from .models import Category, Product, ProductAttribute, ProductAttributeItem, ProductImage

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order', 'caption']

class ProductAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAttribute
        fields = ['id', 'name']

class ProductAttributeItemSerializer(serializers.ModelSerializer):
    attribute_name = serializers.CharField(source='attribute.name', read_only=True)
    attribute_id = serializers.PrimaryKeyRelatedField(
        source='attribute',
        queryset=ProductAttribute.objects.all(),
        write_only=True,
        required=False
    )
    attribute_name_new = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = ProductAttributeItem
        fields = ['id', 'attribute', 'attribute_name', 'attribute_id', 'attribute_name_new', 'value']

    def validate(self, data):
        attribute_id = data.get('attribute', None)
        attribute_name_new = data.get('attribute_name_new', None)
        
        if not attribute_id and not attribute_name_new:
            raise serializers.ValidationError(
                "Either existing attribute_id or new attribute_name_new must be provided"
            )
        if attribute_id and attribute_name_new:
            raise serializers.ValidationError(
                "Cannot provide both attribute_id and attribute_name_new"
            )
        return data

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(source='category_obj', read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        source='category_obj',
        queryset=Category.objects.all(),
        write_only=True
    )
    attributes = ProductAttributeItemSerializer(many=True, read_only=True)
    product_attributes = ProductAttributeItemSerializer(many=True, write_only=True, required=False)
    images = ProductImageSerializer(many=True, read_only=True)
    uploaded_images = serializers.ListField(
        child=serializers.ImageField(max_length=1000000, allow_empty_file=False, use_url=False),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'category_id', 
                 'attributes', 'product_attributes', 'images', 'uploaded_images']

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product_attributes = validated_data.pop('product_attributes', [])
        product = super().create(validated_data)
        
        # Handle product attributes
        for attr_data in product_attributes:
            attribute_name_new = attr_data.pop('attribute_name_new', None)
            if attribute_name_new:
                # Create new attribute if it doesn't exist
                attribute, _ = ProductAttribute.objects.get_or_create(name=attribute_name_new)
                attr_data['attribute'] = attribute
            
            ProductAttributeItem.objects.create(product=product, **attr_data)
        
        # Handle uploaded images
        for order, image in enumerate(uploaded_images):
            ProductImage.objects.create(
                product=product,
                image=image,
                order=order
            )
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product_attributes = validated_data.pop('product_attributes', [])
        product = super().update(instance, validated_data)
        
        # Handle product attributes
        if product_attributes:
            # Clear existing attributes if new ones are provided
            instance.attributes.all().delete()
            for attr_data in product_attributes:
                attribute_name_new = attr_data.pop('attribute_name_new', None)
                if attribute_name_new:
                    # Create new attribute if it doesn't exist
                    attribute, _ = ProductAttribute.objects.get_or_create(name=attribute_name_new)
                    attr_data['attribute'] = attribute
                
                ProductAttributeItem.objects.create(product=instance, **attr_data)
        
        # Handle uploaded images
        if uploaded_images:
            current_order = ProductImage.objects.filter(product=product).count()
            for image in uploaded_images:
                ProductImage.objects.create(
                    product=product,
                    image=image,
                    order=current_order
                )
                current_order += 1
        return product

class ProductDetailSerializer(ProductSerializer):
    class Meta(ProductSerializer.Meta):
        fields = ProductSerializer.Meta.fields