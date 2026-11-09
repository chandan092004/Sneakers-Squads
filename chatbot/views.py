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
        page_context = None
        if request.content_type == 'application/json':
            body = json.loads(request.body.decode('utf-8'))
            message = body.get('message', '').strip()
            page_context = body.get('page_context')
        else:
            message = request.POST.get('message', '').strip()
            page_context = request.POST.get('page_context')

        # Fallback to HTTP Referer to detect current page
        if not page_context:
            referer = request.META.get('HTTP_REFERER', '').lower()
            if '/man' in referer or '/men' in referer:
                page_context = 'man'
            elif '/woman' in referer or '/women' in referer:
                page_context = 'woman'
            elif '/accessor' in referer:
                page_context = 'accessory'
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

    # Pass authenticated user and page_context to engine
    response_data = get_reply(message, user=request.user, page_context=page_context)
    return JsonResponse(response_data)
