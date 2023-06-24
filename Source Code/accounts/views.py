from ast import IsNot
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.message import EmailMessage
from email.policy import default
from gc import get_objects
import re
from urllib import request
from django.forms import EmailField
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import is_valid_path

from accounts.forms import RegistrationForm
from accounts.models import Account, UserProfile
from django.contrib import messages,auth
from django.contrib.auth.decorators import login_required
from orders.models import OrderProduct
from orders.views import Order
from .forms import RegistrationForm,UserForm,UserProfileForm


# verification e
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

from carts.models import Cart
from carts.views import _cart_id, CartItem
from carts.models import Cart,CartItem
import requests



# Create your views here.
def register(request):
    if request.method =='POST':
        form = RegistrationForm(request.POST) # contain all field value
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split('@')[0]


            user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email, username= username, password= password)
            user.phone = phone
            user.save()


            # user veri/acti
            current_site= get_current_site(request)
            mail_subject = 'Please activate your account'
            message= render_to_string('accounts/account_verification.html', {
                'user': user,
                'domain': current_site, 
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)), # hiding primary key
                'token': default_token_generator.make_token(user), # create a token / is a library/ check/make
            })
            to_email = email # send
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

           # messages.success(request, 'Please check your email [..gmail.com] for verification')
            return redirect('/accounts/login/?command=verification&email='+email)
    else:
        form= RegistrationForm()


    
    context= {
        'form': form,

    }
    return render (request, 'accounts/register.html',context)

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email= email, password=password) # return user object
        if user is not None:
            #   CI check
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request)) # get using cart id, checking 
                is_cart_item_exists = CartItem.objects.filter( cart= cart). exists() #uhu
                #print(is_cart_item_exists)
                if  is_cart_item_exists :
                    cart_item = CartItem.objects.filter(cart= cart)
                    
                    #print(cart_item)
                    
                    product_variation= [] # getting the pv by cart id
                    for item in cart_item:
                        variation= item.variations.all()
                        product_variation.append(list(variation)) # query by default
                    
                    # getting cart item to acces cart item form user to access pV
                    cart_item = CartItem.objects.filter( user= user) # create,get for loop
                     #existing variation / from db
                     #current_variation/ product variation list
                     #item_id / from db / if cv is inside existing variation

                    ex_var_list= [] # can be multiple/ existing v list from db
                    id = []
                    for item in cart_item:
                        existing_variation = item.variations.all()
                        ex_var_list.append(list(existing_variation)) # convertes to list cause it a query set
                        id.append(item.id)      
                    #  product_variation= [1, 2,3,4 ,6 ] # can be many items
                    #  ex_var_list = [4,6,3,5]  # both are used to get common product list

                    for pr in product_variation:
                        if pr in ex_var_list:
                            index = ex_var_list.index(pr) # position of common item
                            item_id= id[index]
                            item = CartItem.objects.get(id=item_id)
                            item.quantity += 1
                            item.user= user
                            item.save()
                        else:
                            cart_item = CartItem.objects.filter(cart=cart)
                            for item in cart_item:
                                            
                    #     assign user to a cart item
                                item.user= user
                                item.save()


            
            except:
                pass
            auth.login(request, user)
            messages.success(request, 'You are now logged in')
             # grab previus url from you came
            url = request.META.get('HTTP_REFERER')
            try:
                query = requests.utils.urlparse(url).query
                # print('query ->' , query)
                # print('-------')
                #next = /cart/checkout
                params = dict(x.split('=') for x in query.split('&'))
                # next key c/c = value
                if 'next' in params:
                    nextPage = params['next']
                    return redirect(nextPage)
                

            except:
               return redirect ('dashboard')
             
        else:
            messages.error(request, 'invalid credentials !')
            return redirect ('login')

    return render(request, 'accounts/login.html')
    
    

@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    messages.success(request,"You are logged out")
    return redirect('login')


#messages.success(request, 'You are now logged in ')




# views.activate
# after email send
def activate(request,uidb64, token):
    try :
        
        uid= urlsafe_base64_decode(uidb64).decode() # decode uidb and store in uid/ gives primary key of user
        user= Account._default_manager.get(pk=uid) # return userobj
    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user: None

        
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active= True
        user.save()
        messages.success(request,'Congratulations, Your account has been activated in gharkoPasal')
        return redirect ('login')
    else:
        messages.error(request, 'Invatid activation Link')
        return redirect('register')

    
@login_required(login_url='login')

def dashboard(request):
    orders = Order.objects.order_by('-created_at').filter(user_id= request.user.id, is_ordered= True)
    orders_count = orders.count()
    userprofile= UserProfile.objects.get(user_id= request.user.id)
    context={
        'orders_count': orders_count,
        'userprofile' : userprofile, 
    }
    return render(request, 'accounts/dashboard.html',context)


def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST['email']
        if Account.objects.filter(email= email).exists():
            user = Account.objects.get(email__exact=email)

            #reset password email

            current_site= get_current_site(request)
            mail_subject = 'Reset Your Password'
            message= render_to_string('accounts/reset.html', {
                'user': user,
                'domain': current_site, 
                'uid' : urlsafe_base64_encode(force_bytes(user.pk)), # hiding primary key
                'token': default_token_generator.make_token(user), # create a token / is a library/ check/make
            })
            to_email = email # send
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send()

            messages.success(request, 'reset email has been sent to your email address')
            return redirect('login')

         



        else:
            messages.error(request,'Account Does not exist')
            return redirect('forgotpassword')

    return render(request,'accounts/forgotpassword.html')


def reset_validate(request,uidb64,token):
    try :
        
        uid= urlsafe_base64_decode(uidb64).decode() # decode uidb and store in uid/ gives primary key of user
        user= Account._default_manager.get(pk=uid) # return userobj

    except(TypeError,ValueError,OverflowError,Account.DoesNotExist):
        user: None

    if user is not None and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Please reset your password')
        return redirect ('resetPassword')
    
    else:
        messages.error(request,'This Link has been expired')
        return redirect('login')
    

def resetPassword(request):
    if request.method == 'POST':
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            uid= request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password) # hash format
            user.save()
            messages.success(request, 'Password reset sucessful')
            return redirect('login')

        else:
            messages.error(request,'Password do not match !')
            return redirect('resetPassword')
    
    else:
        return render(request, 'accounts/resetPassword.html')
    

def my_orders(request):
    orders = Order.objects.filter(user= request.user, is_ordered = True).order_by('-created_at') # descending -
    context ={
        'orders':orders,
    }
    return render (request, 'accounts/my_orders.html',context)



def edit_profile(request):
    userprofile = get_object_or_404(UserProfile, user = request.user) # get profile return error
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user) # cause we wanna update not new
        profile_form = UserProfileForm(request.POST,request.FILES, instance=userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request,'Your Profile has been updated')
            return redirect('edit_profile')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = UserProfileForm(instance = userprofile)
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'userprofile': userprofile,

    }


    return render (request, 'accounts/edit_profile.html',context)


@login_required(login_url='login')

def order_detail(request, order_id):
    order_detail = OrderProduct.objects.filter(order__order_number= order_id)
    order = Order.objects.get(order_number= order_id)
    subtotal = 0
    for i in order_detail:
        subtotal += i.product_price *i.quantity

    context= {
        'order_detail': order_detail,
        'order': order,
        'subtotal': subtotal, 
         
    }
    return render(request, 'accounts/order_detail.html',context)
