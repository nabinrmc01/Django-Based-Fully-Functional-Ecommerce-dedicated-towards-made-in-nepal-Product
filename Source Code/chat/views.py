from django.shortcuts import render

from chat.forms import ChatForms
from .models import Chat
from django.contrib import messages
from django.shortcuts import  redirect, render
from orders import models,views


# Create your views here.


def chat(request):
    return render(request,'chat/chat.html')

def send_message(request, product_id):
    url = request.META.get('HTTP_REFERER') # url storet of tab
    if request.method == 'POST':
        try:
            reviews = Chat.objects.get(user__id=request.user.id, product__id= product_id)
            form = ChatForms(request.POST, instance=reviews) # update revie
            form.save()
            messages.success(request,'Thank you your review has been updated')
            return redirect(url)

        except Chat.DoesNotExist:
            form = ChatForms(request.POST)

            if form.is_valid():
                data = Chat()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request,'Thank you your review has been submitted')
                return redirect(url)
                
    




