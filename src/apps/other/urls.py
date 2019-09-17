from apps.other import views as other_views
from core.urls import url


patterns = (
    url(
        method='GET',
        path='/api/specification/',
        handler=other_views.OpenApiSpecificationView,
        name='api:specification',
    ),
)
