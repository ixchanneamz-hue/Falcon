from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=14, decimal_places=6, default=Decimal('0'))
    updated_at = models.DateTimeField(auto_now=True)


class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content_url = models.URLField()
    reward = models.DecimalField(max_digits=12, decimal_places=6, validators=[MinValueValidator(Decimal('0.000001'))])
    watch_seconds = models.PositiveIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


class TaskCompletion(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_completions')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='completions')
    comment = models.TextField()
    rating = models.PositiveSmallIntegerField()
    reward = models.DecimalField(max_digits=12, decimal_places=6)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'task'], name='unique_user_task_completion')]


class Withdrawal(models.Model):
    STATUS_CHOICES = [('pending','قيد المراجعة'),('approved','مقبول'),('rejected','مرفوض'),('paid','تم الدفع')]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=14, decimal_places=6, validators=[MinValueValidator(Decimal('1'))])
    wallet_address = models.CharField(max_length=255)
    network = models.CharField(max_length=20, default='TRC20')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
