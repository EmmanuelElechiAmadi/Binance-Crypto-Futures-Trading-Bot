from django.urls import path
from bots import views


urlpatterns = [
    path('', views.bot_futures_trades_sub, name= 'bot_futures_trades_sub'),
   # path('', views.bot_spots_trades_sub, name= 'bot_spots_trades_sub')

]