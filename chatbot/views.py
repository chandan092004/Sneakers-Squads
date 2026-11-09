import json
from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .engine import get_reply

@csrf_exempt
@require_POST
def chatbot_api(request):
    """
    POST-only API endpoint for Chatbot.
    Accepts JSON body: {"message": "user input query"}
    Returns JSON: {"text": "bot response", "products": [...]}
    """
    try:
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
            message = body.get('message', '').strip()
        else:
            message = request.POST.get('message', '').strip()
    except Exception as e:
        return JsonResponse({
            'text': "Invalid request format. Kripya JSON payload bhejein.",
            'products': []
        }, status=400)

    if not message:
        return JsonResponse({
            'text': "Kripya koi message likhein, jaise: 'Nike under 4000' ya 'Trending sneakers'.",
            'products': []
        })

    # Pass authenticated user (or AnonymousUser) to engine
    response_data = get_reply(message, user=request.user)
    return JsonResponse(response_data)
