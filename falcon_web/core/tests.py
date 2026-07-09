from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import OfferwallProvider, OfferwallTransaction, Task, TaskCompletion, Wallet, Withdrawal

class FalconWebTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='tester', password='StrongPass123!')
        self.wallet = Wallet.objects.create(user=self.user, balance=Decimal('2'))
        self.task = Task.objects.create(title='مهمة اختبار', description='وصف المهمة', content_url='https://example.com', reward=Decimal('0.1'))

    def test_registration_creates_wallet(self):
        response = self.client.post(reverse('register'), {'username':'newuser','password1':'VeryStrongPass123!','password2':'VeryStrongPass123!'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Wallet.objects.filter(user__username='newuser').exists())

    def test_task_reward_is_added_once(self):
        self.client.login(username='tester', password='StrongPass123!')
        url = reverse('complete_task', args=[self.task.id])
        self.client.post(url, {'comment':'تعليق جيد جدا', 'rating':'5'})
        self.client.post(url, {'comment':'تعليق جيد جدا', 'rating':'5'})
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('2.1'))
        self.assertEqual(TaskCompletion.objects.filter(user=self.user, task=self.task).count(), 1)

    def test_withdrawal_minimum_and_balance(self):
        self.client.login(username='tester', password='StrongPass123!')
        self.client.post(reverse('withdraw'), {'amount':'1', 'wallet_address':'TTestAddress'})
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('1'))
        self.assertEqual(Withdrawal.objects.count(), 1)

    def test_offerwall_postback_is_idempotent(self):
        provider = OfferwallProvider.objects.create(name='Test', slug='test', secret_key='secret', is_active=True)
        url = reverse('offerwall_postback', args=['test'])
        payload = {'user_id':self.user.id, 'transaction_id':'tx-1', 'reward':'0.5'}
        self.client.post(url, payload, HTTP_X_POSTBACK_SECRET='secret')
        self.client.post(url, payload, HTTP_X_POSTBACK_SECRET='secret')
        self.wallet.refresh_from_db()
        self.assertEqual(self.wallet.balance, Decimal('2.5'))
        self.assertEqual(OfferwallTransaction.objects.filter(provider=provider, transaction_id='tx-1').count(), 1)
