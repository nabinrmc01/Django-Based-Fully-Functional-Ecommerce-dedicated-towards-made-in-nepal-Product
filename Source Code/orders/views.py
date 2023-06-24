from datetime import datetime
from multiprocessing import context
from .models import Order, OrderProduct, Payment
from django.shortcuts import redirect, render
from carts.models import CartItem
from django.http import HttpResponse, JsonResponse
from .forms import OrderForm
import json
from store.models import Product
from django.core.mail import EmailMessage
from django.template.loader import render_to_string



# Create your views here.
def place_order (request, total =0 ,quantity= 0 ):

    current_user = request.user
    # if cart count <= 0 the redirect back to store
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect ('store')
    
    g_total = 0
    d_charge= 150

    for cart_item in cart_items:
        total+= (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity

    g_total= total+ d_charge

    if request.method == 'POST':

        form = OrderForm(request.POST)

        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data ['first_name']
            data.last_name = form.cleaned_data ['last_name']
            data.phone = form.cleaned_data ['phone']
            data.email = form.cleaned_data ['email']
            data.address1 = form.cleaned_data ['address1']
            data.address2 = form.cleaned_data ['address2']
            
            data.state = form.cleaned_data ['state']
            data.city = form.cleaned_data ['city']
            data.order_note = form.cleaned_data ['order_note']
            
            data.order_total = g_total
            #data.d_charge = form.cleaned_data['d_charge']
            data.ip= request.META.get('REMOTE_ADDR')
            data.save()
            
            # generate order num 
            # yr = int(datetime.date.today().strftime('%Y'))
            # dt = int(datetime.date.today().strftime('%d'))
            # mt = int(datetime.date.today().strftime('%m'))

            # d = datetime.date(yr,dt,mt)
            # current_date = d.strftime("%Y%d%m")
            order_number = "202204" + str(data.id)
            data.order_number = order_number
            data.save()

            
            order = Order.objects.get(user=current_user, is_ordered = False, order_number= order_number)

            context = {
                'order' : order,
                'cart_item': cart_item,
                'total' : total,
                'd_charge' : d_charge,
                'g_total': g_total,
            }
            return render (request, 'orders/payments.html',context)

            
        
        else:
            return HttpResponse('smth wrong i can feel it')
   
   
def payments(request):
    # body_unicode = request.body.decode('utf-8')
    body = json.loads(request.body)
    order = Order.objects.get(user= request.user, is_ordered= False, order_number = body['orderID'])
    # print(body)
    # store in payment model
    payment = Payment(
        user = request.user,
        payment_id = body ['transID'],
        payment_method= body ['payment_method'],
        amount_paid = order.order_total,

        status = body ['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()
    # move cart items to order product
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        orderproduct = OrderProduct()
        orderproduct.order_id = order.id
        orderproduct.payment = payment
        orderproduct.user_id = request.user.id 
        orderproduct.product_id = item.product_id
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.  price
        orderproduct.ordered = True
        orderproduct.save() 

        cart_item = CartItem.objects.get(id = item.id)
        product_variation = cart_item.variations.all()

        orderproduct= OrderProduct.objects.get(id=orderproduct.id)  
        orderproduct.variations.set(product_variation)
        orderproduct.save() 
        #reduce the quantity of sold product

        product = Product.objects.get(id= item.product_id)
        product.stock -= item.quantity
        product.save()
    # clear cart


    CartItem.objects.filter(user=request.user).delete()
    # mail

    mail_subject = 'Thank you for your order'
    message= render_to_string('orders/order_recieve.html', {
        'user': request.user,
        'order' : order,

    })
    to_email = request.user.email # send
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # send order_num and trans id  bavk to sendData method via JsonResponse
    data = {
        'order_number': order.order_number,
        'transID' : payment.payment_id,
    }
    return JsonResponse(data)
    # return render(request,'orders/payments.html')


    



def order_complete(request):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number = order_number, is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        subtotal = 0
        for i  in ordered_products:
            subtotal +=i.product_price * i.quantity


        payment =  Payment.objects.get(payment_id = transID)

        context = {
            'order' : order,
            'ordered_products':ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'payment' : payment,
            'subtotal' : subtotal,
        }
        return render(request, 'orders/order_complete.html',context)
    
    except(Payment.DoesNotExist,Order.DoesNotExist):
        return redirect ('home')
    
    return render(request, 'orders/order_complete.html')

# def khalti_verification(request):
#     data = {}

#     return JsonResponse(data)
    


