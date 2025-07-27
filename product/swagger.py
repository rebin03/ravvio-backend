from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductDetailSerializer,
    ProductAttributeSerializer
)

# Category ViewSet schema definitions
category_schema = extend_schema_view(
    list=extend_schema(description="List all product categories"),
    retrieve=extend_schema(description="Get details of a specific category"),
    create=extend_schema(description="Create a new product category"),
    update=extend_schema(description="Update a product category"),
    partial_update=extend_schema(description="Partially update a product category"),
    destroy=extend_schema(description="Delete a product category")
)

# Product Attribute ViewSet schema definitions
attribute_schema = extend_schema_view(
    list=extend_schema(description="List all product attributes"),
    retrieve=extend_schema(description="Get details of a specific product attribute"),
    create=extend_schema(description="Create a new product attribute"),
    update=extend_schema(description="Update a product attribute"),
    partial_update=extend_schema(description="Partially update a product attribute"),
    destroy=extend_schema(description="Delete a product attribute")
)

# Product ViewSet schema definitions
product_schema = extend_schema_view(
    list=extend_schema(description="List all products"),
    retrieve=extend_schema(description="Get detailed information about a specific product"),
    create=extend_schema(description="Create a new product"),
    update=extend_schema(description="Update a product"),
    partial_update=extend_schema(description="Partially update a product"),
    destroy=extend_schema(description="Delete a product")
)

# Custom action schema definitions
bulk_create_schema = extend_schema(
    description="Create multiple product attributes at once",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "names": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of attribute names to create"
                }
            },
            "required": ["names"]
        }
    },
    responses={201: ProductAttributeSerializer(many=True)}
)

search_or_create_schema = extend_schema(
    description="Search for attributes by name, optionally creating if not found",
    parameters=[
        OpenApiParameter(
            name="name", 
            description="Name to search for", 
            required=True, 
            type=str
        ),
        OpenApiParameter(
            name="create", 
            description="Create attribute if not found (true/false)", 
            required=False, 
            type=bool
        )
    ],
    responses={200: ProductAttributeSerializer(many=True)}
)

add_images_schema = extend_schema(
    description="Add images to a product",
    request={
        "multipart/form-data": {
            "type": "object",
            "properties": {
                "images": {
                    "type": "array",
                    "items": {"type": "string", "format": "binary"},
                    "description": "Product images to upload"
                }
            }
        }
    },
    responses={200: ProductDetailSerializer}
)

update_image_order_schema = extend_schema(
    description="Update the display order of product images",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "image_orders": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Image ID"},
                            "order": {"type": "integer", "description": "New display order"}
                        },
                        "required": ["id", "order"]
                    },
                    "description": "List of image IDs with their new order values"
                }
            },
            "required": ["image_orders"]
        }
    },
    responses={200: ProductDetailSerializer}
)

update_attributes_schema = extend_schema(
    description="Update product attributes in bulk",
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "clear_existing": {
                    "type": "boolean", 
                    "description": "Whether to clear existing attributes before adding new ones"
                },
                "attributes": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer", "description": "Attribute item ID (for updates)"},
                            "attribute": {"type": "integer", "description": "Attribute ID"},
                            "attribute_name_new": {"type": "string", "description": "New attribute name (if creating)"},
                            "value": {"type": "string", "description": "Attribute value"}
                        }
                    },
                    "description": "List of attributes to add or update"
                }
            },
            "required": ["attributes"]
        }
    },
    responses={200: ProductDetailSerializer}
)
