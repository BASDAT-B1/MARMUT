from django.urls import include, path
from melihat_chart.views import show_daily, show_weekly

app_name = 'melihat_chart'

urlpatterns = [
    path('weekly20/', show_weekly, name='show_weekly'),
    path('daily20/', show_daily, name='show_daily')
]