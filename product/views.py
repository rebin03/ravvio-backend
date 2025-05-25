from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product, ProductImage, ProductAttribute
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    ProductImageSerializer,
    ProductAttributeSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Create multiple attributes at once."""
        names = request.data.get('names', [])
        attributes = []
        for name in names:
            attribute, created = ProductAttribute.objects.get_or_create(name=name)
            attributes.append(attribute)
        
        serializer = self.get_serializer(attributes, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def search_or_create(self, request):
        """Search for attributes by name, returns matches or creates if none found."""
        query = request.query_params.get('name', '')
        if not query:
            return Response(
                {"error": "Name parameter is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Search for existing attributes
        attributes = ProductAttribute.objects.filter(name__icontains=query)
        if not attributes.exists() and request.query_params.get('create', 'false').lower() == 'true':
            # Create new attribute if requested
            attribute = ProductAttribute.objects.create(name=query)
            attributes = [attribute]
            
        serializer = self.get_serializer(attributes, many=True)
        return Response(serializer.data)
    
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category_obj']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    @action(detail=True, methods=['post'])
    def add_images(self, request, pk=None):
        product = self.get_object()
        images_data = request.FILES.getlist('images')
        order = ProductImage.objects.filter(product=product).count()
        
        for image_data in images_data:
            ProductImage.objects.create(
                product=product,
                image=image_data,
                order=order
            )
            order += 1
            
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_image_order(self, request, pk=None):
        product = self.get_object()
        image_orders = request.data.get('image_orders', [])
        
        for image_order in image_orders:
            image_id = image_order.get('id')
            new_order = image_order.get('order')
            
            if image_id and new_order is not None:
                try:
                    image = ProductImage.objects.get(id=image_id, product=product)
                    image.order = new_order
                    image.save()
                except ProductImage.DoesNotExist:
                    pass
                    
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def update_attributes(self, request, pk=None):
        """Update product attributes in bulk."""
        product = self.get_object()
        attributes_data = request.data.get('attributes', [])
        
        # Clear existing attributes if specified
        if request.data.get('clear_existing', False):
            product.attributes.all().delete()
        
        created_attributes = []
        for attr_data in attributes_data:
            # Handle new attribute creation
            if 'attribute_name_new' in attr_data:
                attribute, _ = ProductAttribute.objects.get_or_create(
                    name=attr_data['attribute_name_new']
                )
                attr_data['attribute'] = attribute.id
                del attr_data['attribute_name_new']
            
            # Create or update attribute item
            if 'id' in attr_data:
                # Update existing attribute item
                try:
                    attr_item = product.attributes.get(id=attr_data['id'])
                    for key, value in attr_data.items():
                        if key != 'id':
                            setattr(attr_item, key, value)
                    attr_item.save()
                    created_attributes.append(attr_item)
                except ProductAttributeItem.DoesNotExist:
                    pass
            else:
                # Create new attribute item
                attr_item = product.attributes.create(
                    attribute_id=attr_data['attribute'],
                    value=attr_data['value']
                )
                created_attributes.append(attr_item)
        
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
