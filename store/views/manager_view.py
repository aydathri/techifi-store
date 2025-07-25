from store.models import User, Manager, Customer, Category, Product, Review, OrderItem
from store.forms import (ManagerRegisterForm, ManagerLoginForm, ManagerForgotPasswordForm,
                         ManagerResetPasswordForm, ManagerEditProfileForm, CategoryForm, ProductForm)
import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required
from django.views.decorators .http import require_GET
from django.db.models import Q

def ManagerSingUpView(request):
    form = ManagerRegisterForm()

    if request.method == 'POST':
        form = ManagerRegisterForm(request.POST)
        if form.is_valid():
            request.session['user_data']={
                'username': form.cleaned_data['username'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                'password1': form.cleaned_data['password1'],
                'password2': form.cleaned_data['password2'],
            }

            token = str(random.randint(100000, 999999))
            request.session['verify_token'] = token

            send_mail(
                'Verification Code',
                f'Your verification code is: {token}',
                settings.EMAIL_HOST_USER,
                [form.cleaned_data['email']],
                fail_silently=False,
            )

            messages.success(request, "Please check your email for the verification code.")
            return redirect('manager-verify-login-token')
    else:
        form = ManagerRegisterForm()

    return render(request, 'manager/sign_up.html', {'form': form})



def ManagerVerifyTokenView(request):
    User = get_user_model()

    if request.method == 'POST':
        session_token = request.session.get('verify_token')
        temp_data = request.session.get('user_data')
        input_token = request.POST.get('token')

        if not session_token or not temp_data:
            messages.error(request, 'Please register first.')
            return redirect('manager-sign-up')

        if input_token == session_token:
            user = User(
                username = temp_data['username'],
                first_name = temp_data['first_name'],
                last_name = temp_data['last_name'],
                email = temp_data['email'],
                phone = temp_data['phone'],
                is_active = True,
                is_staff = True,
            )

            user.set_password(temp_data['password1'])
            user.save()

            Manager.objects.create(user = user)

            del request.session['user_data']
            del request.session['verify_token']

            messages.success(request, 'Your registration has been successfully confirmed! You can now log in.')
            return redirect('manager-login')


        else:
            messages.error(request, 'The activation code is incorrect.')

    return render(request, 'manager/verify_login_token.html')



def ManagerLoginView(request):
    form = ManagerLoginForm()

    if request.method == 'POST':
        form = ManagerLoginForm(request.POST)

        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            user_auth = None

            if User.objects.filter(email = identifier, is_staff = True).exists():
                try:
                    user = User.objects.get(email = identifier)
                    user_auth = authenticate(request, username = user.username, password = password)
                except User.DoesNotExist:
                    user = None

            else:
                user_auth = authenticate(request, username = identifier, password = password)

            if user_auth is not None and Manager.objects.filter(user = user_auth).exists():
                request.session['user-id'] = user_auth.id
                login(request, user_auth)
                messages.success(request, 'You are now logged in.')
                return redirect('manager-dashboard')

            else:
                messages.error(request, 'Invalid username/email or password')

    return render(request, 'manager/login.html', {'form' : form})



def ManagerForgotPasswordView(request):
    form = ManagerForgotPasswordForm()

    if request.method == 'POST':
        form = ManagerForgotPasswordForm(request.POST)

        if form.is_valid():
            identifier = form.cleaned_data['identifier']

            user = (Manager.objects.filter(user__username = identifier).first() or
                    Manager.objects.filter(user__email = identifier).first())

            if user:
                token = random.randint(100000, 999999)
                cache.set(f'password-reset-token-{user.user.id}', token, timeout = 300)

                send_mail(
                    subject = 'Forgot Password',
                    message = f'Your password reset token: {token}',
                    from_email = settings.EMAIL_HOST_USER,
                    recipient_list = [user.user.email],
                    fail_silently = False
                )

                request.session['user-id'] = user.user.id
                messages.success(request, 'Token has been sent to your email.')
                return redirect('manager-verify-password-token')

            else:
                messages.error(request, 'User not found')

    return render(request, 'manager/forgot_password.html', {'form' : form})



def ManagerVerifyForgotPasswordTokenView(request):
    if request.method == 'POST':
        token_input = request.POST.get('token')
        user_id = request.session.get('user-id')

        if not user_id:
            messages.error(request, 'Session expired. Please request a new code.')
            return redirect('manager-forgot-password')

        cache_key = f'password-reset-token-{user_id}'
        cache_token = cache.get(cache_key)

        if not cache_token:
            messages.error(request, 'Token has expired. Please request a new one.')
            return redirect('manager-forgot-password')

        if int(token_input) == cache_token:
            return redirect('manager-reset-password')

        else:
            messages.error(request, 'Invalid token.Please try again.')

    return render(request, 'manager/verify_password_token.html')



def ManagerResetPasswordView(request):
    form = ManagerResetPasswordForm()

    if request.method == 'POST':
        form = ManagerResetPasswordForm(request.POST)

        if form.is_valid():
            user_id = request.session.get('user-id')

            if not user_id:
                messages.error(request, 'Session expired. Please request a new code.')
                return redirect('manager-forgot-password')

            user = Manager.objects.get(user__id = user_id)

            if user:
                new_password = form.cleaned_data['new_password']
                user.user.set_password(new_password)
                user.user.save()

                cache.delete(f'password-reset-token-{user_id}')
                del request.session['user-id']

                messages.success(request, 'Your password has been reset.You can now log in.')
                return redirect('manager-login')

            else:
                messages.error(request, 'User not found')
                return redirect('manager-forgot-password')

    return render(request, 'manager/reset_password.html', {'form' : form})



@login_required()
def ManagerDashboarView(request):
    return render(request, 'manager/dashboard.html')


@login_required()
def ManagerEditProfileView(request):
    user = request.user
    if request.method == 'POST':
        form = ManagerEditProfileForm(request.POST, request.FILES, instance=user)

        if form.is_valid():
            phone = form.cleaned_data['phone']
            if len(phone) != 11:
                messages.error(request, 'The number must be 11 digits.')
            else:
                form.save()

            messages.success(request, 'Profile updated successfully.')
            return redirect('manager-profile')

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = ManagerEditProfileForm(instance=user)

    return render(request, 'manager/profile.html', {'form': form})



@require_GET
def ManagerShowCustomersView(request):
    search_query = request.GET.get('search_query', '')
    if search_query:
        customers = Customer.objects.filter(
            Q(user__username__exact=search_query) |
            Q(user__phone__exact=search_query)
        )
        if not customers:
            messages.error(request, 'No customers found.')

    else:
        customers = Customer.objects.all()
    context = {'customers': customers,
               'search_query': search_query}
    return render(request, 'manager/customer.html', context)



def ManagerCustomerDelete(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer.user.delete()
    customer.delete()
    messages.success(request, 'User deleted')
    return redirect('manager-show-customer')



def CategoryView(request):
    categories = Category.objects.all()
    form = CategoryForm()

    if request.method == 'POST':
        if 'add_category' in request.POST:
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('manage-categories')

        elif 'edit_category' in request.POST:
            cat_id = request.POST.get('cat_id')
            category = get_object_or_404(Category, id=cat_id)
            form = CategoryForm(request.POST, instance=category)
            if form.is_valid():
                form.save()
                return redirect('manage-categories')

        elif 'delete_category' in request.POST:
            cat_id = request.POST.get('cat_id')
            category = get_object_or_404(Category, id=cat_id)
            category.delete()
            return redirect('manage-categories')

    return render(request, 'manager/category.html', {
        'form': form,
        'categories': categories,
    })




@login_required()
def ProductView(request):
    search_query = request.GET.get('search_query', '')
    category_id = request.GET.get('category', '')

    products = Product.objects.all()
    if search_query:
        products = products.filter(Q(title__icontains = search_query))
    if category_id:
        products = products.filter(category_id = category_id)

    form = ProductForm()
    categories = Category.objects.all()

    if request.method == 'POST':
        if 'add_product' in request.POST:
            form = ProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, 'Product added successfully.')
                return redirect('manage-products')


        elif 'edit_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            if request.POST.get('remove_image') == 'on' and product.image:
                product.image.delete(save=False)
                product.image = None
                product.save()

            if request.POST.get('title'):
                product.title = request.POST.get('title')

            if request.POST.get('description'):
                product.description = request.POST.get('description')

            if request.POST.get('price'):
                product.price = request.POST.get('price')

            if request.POST.get('category'):
                product.category_id = request.POST.get('category')

            if request.POST.get('is_active'):
                product.is_active = request.POST.get('is_active')

            if request.FILES.get('image'):
                product.image = request.FILES['image']

            product.save()
            messages.success(request, 'Product updated successfully.')
            return redirect('manage-products')

        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            product = get_object_or_404(Product, id=product_id)
            product.delete()
            messages.success(request, 'Product deleted successfully.')
            return redirect('manage-products')

    return render(request, 'manager/product.html', {'form': form,
                                                                        'products': products,
                                                                        'categories': categories,
                                                                        'search_query': search_query,
                                                                        'selected_category': category_id})




@login_required()
def ReviewView(request):
    search_query = request.GET.get('search_query', '')
    category_id = request.GET.get('category', '')
    product_id = request.GET.get('product_id', '')

    reviews = Review.objects.select_related('user', 'product', 'product__category').all()

    if search_query.isdigit():
        reviews = reviews.filter(score = int(search_query))
    if category_id:
        reviews = reviews.filter(product__category_id = category_id)
    if product_id:
        reviews = reviews.filter(product_id = product_id)

    categories = Category.objects.all()
    products = Product.objects.all()

    if request.method == 'POST' and 'delete_review' in request.POST:
            review_id = request.POST.get('review_id')
            review = get_object_or_404(Review, id=review_id)
            review.delete()
            messages.success(request, 'Review deleted successfully.')
            return redirect('manage-reviews')

    return render(request, 'manager/review.html', {'reviews': reviews,
                                                                       'search_query': search_query,
                                                                       'selected_category': category_id,
                                                                       'selected_product': product_id,
                                                                       'categories': categories,
                                                                       'products': products,})




@login_required()
def OrderView(request):
    search_query = request.GET.get('search_query', '')
    selected_category = request.GET.get('category', '')
    selected_product = request.GET.get('product', '')

    order_items = OrderItem.objects.select_related('order', 'product', 'order__user').all()
    if search_query:
        order_items = order_items.filter(
            Q(order__user__username__icontains = search_query) |
            Q(order__user__email__icontains = search_query) |
            Q(product__title__icontains = search_query) |
            Q(product__category__title__icontains = search_query) |
            Q(status__icontains = search_query) |
            Q(order__is_paid__icontains = search_query)
        )

    if selected_category:
        order_items = order_items.filter(product__category__id = selected_category)
    if selected_product:
        order_items = order_items.filter(product__id = selected_product)

    categories = Category.objects.all()
    products = Product.objects.all()

    if request.method == 'POST':
        if 'update_status' in request.POST:
            item_id = request.POST.get('item_id')
            new_status = request.POST.get('new_status')
            item = get_object_or_404(OrderItem, id = item_id)
            item.status = new_status
            item.save()
            messages.success(request, 'Status update successfully')
            return redirect('manager-orders')

        elif 'delete_item' in request.POST:
            item_id = request.POST.get('item_id')
            item = get_object_or_404(OrderItem, id = item_id)
            item.delete()
            messages.success(request, 'Item delete successfully')
            return redirect('manager-orders')

    return render(request, 'manager/order.html', {'order_items': order_items,
                                                                     'search_query': search_query,
                                                                     'selected_category': selected_product,
                                                                     'selected_product': selected_product,
                                                                     'categories': categories,
                                                                     'products': products})




@login_required()
def LogoutView(request):
    logout(request)
    return redirect('global-home')