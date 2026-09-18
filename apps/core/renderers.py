import json

from rest_framework.renderers import JSONRenderer


class ApiRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get("response") if renderer_context else None
        status_code = response.status_code if response else 200

        # Error responses already have the correct shape from the exception handler
        if status_code >= 400:
            envelope = data
        else:
            envelope = {
                "success": True,
                "data": data,
                "status_code": status_code,
            }

        return super().render(envelope, accepted_media_type, renderer_context)
