import hmac
from decimal import Decimal, InvalidOperation
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import OfferwallProvider, OfferwallTransaction, Wallet

@csrf_exempt
@require_POST
def offerwall_postback(request, provider_slug):
    provider = OfferwallProvider.objects.filter(slug=provider_slug, is_active=True).first()
    if not provider:
        return HttpResponse(status=404)
    supplied = request.headers.get('X-Postback-Secret', '')
    if not hmac.compare_digest(supplied, provider.secret_key):
        return HttpResponse(status=403)
    user_id = request.POST.get('user_id', '')
    transaction_id = request.POST.get('transaction_id', '').strip()
    try:
        reward = Decimal(request.POST.get('reward', '0'))
    except InvalidOperation:
        return JsonResponse({'ok': False, 'error': 'invalid_reward'}, status=400)
    if not transaction_id or reward <= 0:
        return JsonResponse({'ok': False, 'error': 'invalid_payload'}, status=400)
    user = get_user_model().objects.filter(pk=user_id).first()
    if not user:
        return JsonResponse({'ok': False, 'error': 'unknown_user'}, status=404)
    try:
        with transaction.atomic():
            OfferwallTransaction.objects.create(provider=provider, user=user, transaction_id=transaction_id, reward=reward)
            wallet, _ = Wallet.objects.select_for_update().get_or_create(user=user)
            wallet.balance += reward
            wallet.save(update_fields=['balance', 'updated_at'])
    except IntegrityError:
        return JsonResponse({'ok': True, 'duplicate': True})
    return JsonResponse({'ok': True, 'duplicate': False})
