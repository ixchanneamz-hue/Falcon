from decimal import Decimal
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from .models import Task, TaskCompletion, Wallet, Withdrawal


def home(request):
    return render(request, 'core/home.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        Wallet.objects.get_or_create(user=user)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'registration/register.html', {'form': form})


@login_required
def dashboard(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.user)
    return render(request, 'core/dashboard.html', {'balance': wallet.balance, 'completed_tasks': request.user.task_completions.count(), 'referrals': 0})


@login_required
def tasks(request):
    completed_ids = request.user.task_completions.values_list('task_id', flat=True)
    return render(request, 'core/tasks.html', {'tasks': Task.objects.filter(is_active=True).exclude(id__in=completed_ids)})


@login_required
@transaction.atomic
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, is_active=True)
    if request.method != 'POST':
        return render(request, 'core/complete_task.html', {'task': task})
    comment = request.POST.get('comment', '').strip()
    try:
        rating = int(request.POST.get('rating', '0') or 0)
    except ValueError:
        rating = 0
    if len(comment.split()) < 3 or rating not in range(1, 6):
        messages.error(request, 'اكتب تعليقًا من 3 كلمات على الأقل واختر تقييمًا صحيحًا.')
        return redirect('complete_task', task_id=task.id)
    completion, created = TaskCompletion.objects.get_or_create(user=request.user, task=task, defaults={'comment': comment, 'rating': rating, 'reward': task.reward})
    if created:
        wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
        wallet.balance += task.reward
        wallet.save(update_fields=['balance', 'updated_at'])
        messages.success(request, 'تم إكمال المهمة وإضافة المكافأة إلى رصيدك.')
    return redirect('tasks')


@login_required
@transaction.atomic
def withdraw(request):
    wallet, _ = Wallet.objects.select_for_update().get_or_create(user=request.user)
    if request.method == 'POST':
        try:
            amount = Decimal(request.POST.get('amount', '0'))
        except Exception:
            amount = Decimal('0')
        address = request.POST.get('wallet_address', '').strip()
        if amount < Decimal('1') or amount > wallet.balance or not address:
            messages.error(request, 'تحقق من المبلغ والعنوان. الحد الأدنى للسحب هو 1 USDT.')
        else:
            Withdrawal.objects.create(user=request.user, amount=amount, wallet_address=address)
            wallet.balance -= amount
            wallet.save(update_fields=['balance', 'updated_at'])
            messages.success(request, 'تم إرسال طلب السحب للمراجعة.')
            return redirect('dashboard')
    return render(request, 'core/withdraw.html', {'balance': wallet.balance})
