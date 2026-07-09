from django.contrib import admin
from .models import Task, TaskCompletion, Wallet, Withdrawal

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'reward', 'watch_seconds', 'is_active', 'created_at')
    list_filter = ('is_active',)

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'network', 'status', 'created_at')
    list_filter = ('status', 'network')

admin.site.register(Wallet)
admin.site.register(TaskCompletion)
