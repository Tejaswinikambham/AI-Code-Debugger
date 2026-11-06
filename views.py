import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .Workflow import run_tutor_workflow

MAX_CODE_CHARS = 20_000


@csrf_exempt  # For a local API demo only; add authentication and CSRF protection before deployment.
def analyze_code(request):
    if request.method != "POST":
        return JsonResponse({"error": "Use POST with JSON."}, status=405)
    try:
        payload = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    code = payload.get("code") if isinstance(payload, dict) else None
    if not isinstance(code, str) or not code.strip():
        return JsonResponse({"error": "Provide non-empty code as a string."}, status=400)
    if len(code) > MAX_CODE_CHARS:
        return JsonResponse({"error": f"Code must be at most {MAX_CODE_CHARS} characters."}, status=413)

    return JsonResponse(run_tutor_workflow(code))
