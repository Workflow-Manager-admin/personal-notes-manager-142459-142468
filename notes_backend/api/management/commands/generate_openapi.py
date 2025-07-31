import json
import os

from django.core.management.base import BaseCommand
from django.test import RequestFactory
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny

class Command(BaseCommand):
    help = "Generate the OpenAPI schema for all documented endpoints and models."

    def handle(self, *args, **options):
        """
        Generate and write the OpenAPI schema from all DRF-YASG-documented endpoints.
        """
        factory = RequestFactory()
        django_request = factory.get('/api/?format=openapi')

        # Build schema view with consistent API meta
        schema_view = get_schema_view(
            openapi.Info(
                title="My API",
                default_version='v1',
                description="Test description",
            ),
            public=True,
            permission_classes=(AllowAny,),
        )

        # Render OpenAPI schema as JSON
        response = schema_view.without_ui(cache_timeout=0)(django_request)
        response.render()

        openapi_schema = json.loads(response.content.decode())

        output_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "interfaces"
        )
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "openapi.json")

        with open(output_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)
