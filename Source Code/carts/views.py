import imp
from importlib.resources import contents
from multiprocessing import context
from operator import index
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from store.models import Product, Variation
from carts.models import Cart, CartItem
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required





# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart (request, product_id):
    #current_user_variable
    current_user = request.user 
    product = Product.objects.get(id= product_id) # get product 
    # if the user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.method  == 'POST':
            for item in request.POST:
                key= item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact= key,variation_value__iexact= value) # ignore if key is capital or small
                    #print (variation)
                    product_variation.append(variation)
                except: 
                    pass



        is_cart_item_exists = CartItem.objects.filter(product= product, user= current_user). exists() #uhu
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product= product, user = current_user) # create,get for loop
            #existing variation / from db
            #current_variation/ product variation list
            #item_id / from db / if cv is inside existing variation

            ex_var_list= [] # can be multiple/ existing v list from db
            id = []

            for item in cart_item:
                # increase cart item quaantity

                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation)) # convertes to list cause it a query set
                id.append(item.id)


            if product_variation in ex_var_list:
                # return HttpResponse('true')
                #increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id= id[index]
                item =  CartItem.objects.get(product= product, id= item_id)
                item.quantity += 1
                item.save()
            
            else:
            # return HttpResponse('false')
            # create a new cart item
                item= CartItem.objects.create(product=product,quantity=1, user = current_user)

                if len(product_variation)>0:  # check empty

                    item.variations.clear()
                    item.variations.add(*product_variation)               
            #cart_item.quantity += 1  
                item.save()


        else :
            cart_item = CartItem.objects.create(

                product = product,
                quantity = 1, 
                user = current_user,    


            )
            if len(product_variation)>0:  # check empty
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 

            cart_item.save()
        return redirect('cart')
            
        

                
# if the user is not authenticated
    else:
        product_variation = [] # empty list contains variation small blue
        if request.method  == 'POST':
            # color = request.POST['color']
            # size = request.POST['size']

            for item in request.POST:
                key= item
                value = request.POST[key]
                
                try:
                    variation = Variation.objects.get(product=product,variation_category__iexact= key,variation_value__iexact= value) # ignore if key is capital or small
                    #print (variation)
                    product_variation.append(variation)
                except: 
                    pass
                    
            # return HttpResponse(color+ ' '+ size)
            # exit()


    
        try:
            cart = Cart.objects.get(cart_id=_cart_id (request)) # get cart using from cart id  present in session
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )

        cart.save()


        is_cart_item_exists = CartItem.objects.filter(product= product, cart= cart). exists() #uhu
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product= product, cart= cart) # create,get for loop
            #existing variation / from db
            #current_variation/ product variation list
            #item_id / from db / if cv is inside existing variation

            ex_var_list= [] # can be multiple/ existing v list from db
            id = []

            for item in cart_item:
                # increase cart item quaantity

                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation)) # convertes to list cause it a query set
                id.append(item.id)

            print(ex_var_list)
            
            if product_variation in ex_var_list:
                # return HttpResponse('true')
                #increase the cart item quantity
                index = ex_var_list.index(product_variation)
                item_id= id[index]
                item =  CartItem.objects.get(product= product, id= item_id)
                item.quantity += 1
                item.save()
            
            else:
            # return HttpResponse('false')
            # create a new cart item
                item= CartItem.objects.create(product=product,quantity=1, cart = cart)

                if len(product_variation)>0:  # check empty

                    item.variations.clear()
                    item.variations.add(*product_variation)               
            #cart_item.quantity += 1  
                item.save()


        else :
            cart_item = CartItem.objects.create(

                product = product,
                quantity = 1, 
                cart = cart,


            )
            if len(product_variation)>0:  # check empty
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation) 

            cart_item.save()
        return redirect('cart')

def remove_cart(request, product_id, cart_item_id):
    
    product= get_object_or_404(Product, id= product_id)
    try: 
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product= product, user=request.user, id=cart_item_id)
        else:
            cart= Cart.objects.get(cart_id= _cart_id(request))  
            cart_item = CartItem.objects.get(product= product, cart=cart, id=cart_item_id)



        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass

    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    
    product= get_object_or_404 (Product, id= product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product=product, user=request.user, id= cart_item_id)
    else:
        cart= Cart.objects.get(cart_id= _cart_id(request))
        cart_item = CartItem.objects.get(product=product, cart=cart, id= cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(request, total =0 ,quantity= 0 , cart_items= None):
    try:
        if request.user.is_authenticated:
            cart_items= CartItem.objects.filter(user=request.user, is_active= True)
        else: 

            cart= Cart.objects.get(cart_id=  _cart_id(request))
            cart_items= CartItem.objects.filter(cart=cart, is_active= True)

        for cart_item in cart_items:
            total+= (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
        d_charge= 150
        g_total= total+ d_charge

    except ObjectDoesNotExist :
        pass # just ignore

    context = {
            'total': total,
            'quantity': quantity,
            'cart_items': cart_items,
            'd_charge' :   d_charge,
            'g_total':     g_total,
        }

 
    
    
    return render(request, 'store/cart.html',context)
 


@login_required(login_url='login')       
def checkout(request, total =0 ,quantity= 0 , cart_items= None,):
    try:
        d_charge = (150)
        g_total= d_charge+ total

        if request.user.is_authenticated:
            cart_items= CartItem.objects.filter(user=request.user, is_active= True)
        else: 

            cart= Cart.objects.get(cart_id=  _cart_id(request))
            cart_items= CartItem.objects.filter(cart=cart, is_active= True)

        for cart_item in cart_items:
            total+= (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
         
        
    except ObjectDoesNotExist:
        pass

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'd_charge' :   d_charge,
        'g_total':     g_total,

    }

    
    return render(request,'store/checkout.html',context)

        
            
            

    
        
    
    
    
    
   
        
            
         