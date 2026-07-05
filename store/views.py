
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from accounts.models import Seller
from products.models import Product, Product_picturs
from .forms import ProductForm, ProductPictureForm
from django.contrib import messages


# Create your views here.

def buyer_dashboard(request):
    products = Product.objects.all()
    context = {'products': products}
    return render(request, 'store/buyer_dashboard.html', context)

def cart(request):
    context = {}
    return render(request, "store/cart.html", context)

def checkout(request):
    context = {}
    return render(request, "store/checkout.html", context)



@login_required
def seller_dashboard(request):
    # Ensure the logged-in user is a seller
    if request.user.role != request.user.Role.SELLER:
        return redirect("buyer_dashboard")  # or raise PermissionDenied

    seller = Seller.objects.get(user=request.user)

    products = Product.objects.filter(
        seller=seller
    ).order_by("-id")

    form = ProductForm()

    context = {
        "seller": seller,
        "products": products,
        "product_form": ProductForm(),
        "picture_form": ProductPictureForm(),
    }
        

    return render(request, "store/seller_dashboard.html", context)


@login_required
def add_product(request):

    print(request.POST)
    print(request.FILES)

    if request.method != "POST":
        return redirect("seller_dashboard")

    if request.user.role != request.user.Role.SELLER:
        messages.error(request, "Only sellers can add products.")
        return redirect("buyer_dashboard")

    seller = Seller.objects.get(user=request.user)

    product_form = ProductForm(request.POST)



    if product_form.is_valid():

        product = product_form.save(commit=False)
        product.seller = seller
        product.save()

        pictures = request.FILES.getlist("pictures")

        for index, image in enumerate(pictures):

            Product_picturs.objects.create(
                product=product,
                picture=image,
                is_default=(index == 0)
            )

        messages.success(request, "Product added successfully.")

        return redirect("seller_dashboard")

    messages.error(request, "Please correct the errors in the form.")

    return redirect("seller_dashboard")
