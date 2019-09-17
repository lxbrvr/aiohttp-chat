import yaml

from aiohttp.web_response import json_response, Response

from core import views as core_views
from conf import settings


class OpenApiSpecificationView(core_views.ApiView):
    async def get(self) -> Response:
        with open(settings.API_SPECIFICATION_PATH) as spec:
            loaded_spec = yaml.load(spec)
        return json_response(data=loaded_spec)
