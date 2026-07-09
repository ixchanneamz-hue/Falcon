from django.contrib import admin
from .models import OfferwallProvider, OfferwallTransaction, Task, TaskCompletion, Wallet, Withdrawal

admin.site.site_header = 'إدارة منصة Falcon'
admin.site.site_title = 'Falcon Admin'
admin.site.index_title = 'لوحة الإدارة'

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title','reward','watch_seconds','is_active','created_at')
    list_filter = ('is_active',)
    search_fields = ('title','description')

@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ('user','amount','network','status','created_at')
    list_filter = ('status','network')
    search_fields = ('user__username','wallet_address')
    list_editable = ('status',)

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user','balance','updated_at')
    search_fields = ('user__username',)

@admin.register(TaskCompletion)
class TaskCompletionAdmin(admin.ModelAdmin):
    list_display = ('user','task','reward','rating','completed_at')
    search_fields = ('user__username','task__title','comment')

@admin.register(OfferwallProvider)
class OfferwallProviderAdmin(admin.ModelAdmin):
    list_display = ('name','slug','is_active','created_at')
    list_editable = ('is_active',)

@admin.register(OfferwallTransaction)
class OfferwallTransactionAdmin(admin.ModelAdmin):
    list_display = ('provider','user','transaction_id','reward','created_at')
    search_fields = ('transaction_id','user__username')
