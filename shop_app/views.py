from django.shortcuts import render
from django.views.generic import TemplateView , CreateView , UpdateView , DetailView ,ListView, DeleteView
from django.http import HttpResponse
from shop_app.forms import ProfileForm,UserForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate , login , logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from shop_app.models import  Profile,Medicine,Cart, Orders
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings


# Create your views here.
class Index(TemplateView):
    template_name='shop_app/index.html'

class Aboutus(TemplateView):
    template_name='shop_app/AboutUs.html'



def Register(request):
    Registered=False
    if request.method=='POST':
        profile_form=ProfileForm(request.POST)
        user_form=UserForm(request.POST)
        if profile_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            profile=profile_form.save(commit=False)
            profile.user=user
            profile.save()
            Registered=True
        else:
            return HttpResponse('Invalid Login Id or Password')
    else:
        profile_form=ProfileForm
        user_form=UserForm
    return render(request,'shop_app/registration.html',{'Registered':Registered,'profile_form':profile_form,'user_form':user_form})

def User_login(request):
    if request.method=='POST':
        user_name=request.POST.get('username')
        password=request.POST.get('password')

        user=authenticate(username=user_name,password=password)
        if user:
            if user.is_active:
                print(user.id)
                request.session['id'] = user.id
                login(request,user)
                return redirect('shop_app:index')
                print('successfull')
            else:
                return HttpResponse('INVALID USERNAME OR PASSWORD')
        else:
            return HttpResponse('Invalid Login')
            print("SORRY WE CAN'T LET YOU LOG IN")
    else:
        return render(request,'shop_app/login.html',{})

@login_required
def user_logout(request):
    logout(request)
    return redirect('shop_app:index')
class Stocklist(LoginRequiredMixin,ListView):
    model=Medicine
    context_object_name="stock_list"
    template_name="shop_app/medicine_list.html"



class Stockdetail(LoginRequiredMixin,DetailView):
    model=Medicine
    context_object_name="stock_detail"
    template_name='shop_app/medicine_detail.html'

class Createstock(LoginRequiredMixin,CreateView):
    model=Medicine
    fields=('Shop','Name','Salt','Company','MRP','MFD','Expiry')
    login_url='/login/'
    redirect_field_name="shop_app/medicine_detail.html"


class StockUpdateView(LoginRequiredMixin,UpdateView):
    model=Medicine
    fields=('Shop','Name','Salt','Company','MRP','MFD','Expiry')
    template_name="shop_app/medicine_form.html"
    login_url='/login/'
    redirect_field_name="shop_app/medicine_detail.html"


class StockDeleteView(LoginRequiredMixin,DeleteView):
    model=Medicine
    success_url=reverse_lazy("shop_app:StockList")
    template_name="shop_app/medicine_confirm_delete.html"
    login_url='/login/'
    redirect_field_name="shop_app/medicine_detail.html"


class SearchResultView(ListView):
    model=Medicine
    template_name="shop_app/Searchpage.html"
    def get_queryset(self):
        query=self.request.GET.get('q')
        object_list= Medicine.objects.filter(
         Q(Name__icontains=query) | Q(Salt__icontains=query) | Q(MFD__icontains=query) | Q(Expiry__icontains=query)
        )
        return object_list

def addToCart(request, pk):
    u = User.objects.get(id=request.session['id'])
    p = Profile.objects.get(user=u)
    m = Medicine.objects.get(id=pk)
    if Cart.objects.filter(user=p, medicine=m).exists():
        i = Cart.objects.get(user=p, medicine=m)
        c = i.quantity + 1
        i.quantity = c
        i.save()
    else:
        item = Cart.objects.create(user=p, medicine=m)
        item.save()
    return redirect('/stock/list/')

def myCart(request):
    u = User.objects.get(id=request.session['id'])
    p = Profile.objects.get(user=u)
    items = Cart.objects.filter(user=p)
    return render(request, 'shop_app/myCart.html', {'items':items})

def removeFromCart(request, pk):
    item = Cart.objects.get(id=pk)
    c = item.quantity - 1
    if c == 0:
        item.delete()
    else:
        item.quantity = c
        item.save()
    return redirect('/myCart')

def checkout(request, pk):
    items = Cart.objects.filter(id=pk)
    return render(request, 'shop_app/checkout.html', {'items':items})

def  newOrder(request, pk):
    item = Cart.objects.get(id=pk)
    o = Orders.objects.create(user=item.user, medicine=item.medicine, quantity=item.quantity)
    o.save()

    subject = 'ORDER CONFIRMATION'
    message = 'Your order of \n Product : '+ item.medicine.Name + '\n Price : '+ str(item.medicine.MRP) + '\n is confirmed'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [item.user.user.email,]
    send_mail( subject, message, email_from, recipient_list )

    return render(request, 'shop_app/confirm.html')


def myOrders(request):
    u = User.objects.get(id=request.session['id'])
    p = Profile.objects.get(user=u)
    items = Orders.objects.filter(user=p).order_by('-time')
    return render(request, "shop_app/myOrders.html", {'items':items})
