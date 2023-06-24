from . import views
from django.urls import path, include 


urlpatterns = [
    

    path('send_message/<int:product_id>/', views.send_message, name = 'send_message'),

] 
 