from django.urls import path
from .views import CurrencyRatesView, CurrencyRateByCodeView

urlpatterns = [
    path('rates/<str:date>/', CurrencyRatesView.as_view(), name='currency_rates'),
    path('rate/<str:date>/<str:code>/', CurrencyRateByCodeView.as_view(), name='currency_rate_by_code'),
]
