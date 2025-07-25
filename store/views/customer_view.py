import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from store.forms import (CustomerSignUpForm, CustomerLoginForm, CustomerForgotPasswordForm,
                         CustomerResetPasswordForm, CustomerProfileForm, CustomerReviewForm)
from store.models import Customer, User, OrderItem, Order, Product, Review
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login, logout
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

def SignUpView(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
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
            return redirect('customer-verify-login-token')

    else:
        form = CustomerSignUpForm()

    return render(request, 'customer/sign_up.html', {'form': form})



def VerifyTokenView(request):
    User = get_user_model()

    if request.method == 'POST':
        token_input = request.POST.get('token')
        session_token = request.session.get('verify_token')
        temp_data = request.session.get('user_data')

        if not session_token or not temp_data:
            messages.error(request, 'Please register first.')
            return redirect('customer-sign-up')

        if token_input == session_token:
            user = User(
                username = temp_data['username'],
                first_name = temp_data['first_name'],
                last_name = temp_data['last_name'],
                email = temp_data['email'],
                phone = temp_data['phone'],
                is_active = True,
            )
            if temp_data['password1'] == temp_data['password2']:
                user.set_password(temp_data['password1'])
                user.save()

                Customer.objects.create(user=user)

                del request.session['user_data']
                del request.session['verify_token']

                messages.success(request, 'Your registration has been successfully confirmed! You can now log in.')
                return redirect('customer-login')
            else:
                messages.error(request, 'Passwords do not match.')
                return redirect('customer-sign-up')
        else:
            messages.error(request, 'The activation code is incorrect.')

    return render(request, 'customer/verify_login_token.html')



def LoginView(request):
    form = CustomerLoginForm()

    if request.method == 'POST':
        form = CustomerLoginForm(request.POST)

        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']

            user_auth = None

            if User.objects.filter(email=identifier).exists():
                try:
                    user = User.objects.get(email = identifier)
                    user_auth = authenticate(request, username=user.username, password=password)
                except User.DoesNotExist:
                    user = None

            else:
                user_auth = authenticate(request, username=identifier, password=password)

            if user_auth is not None and Customer.objects.filter(user=user_auth).exists():
                login(request, user_auth)
                messages.success(request, 'You are now logged in.')
                return redirect('global-home')

            else:
                messages.error(request, 'Invalid username/email or password')

    return render(request, 'customer/login.html', {'form': form})



def ForgotPasswordView(request):
    form = CustomerForgotPasswordForm()

    if request.method == 'POST':
        form = CustomerForgotPasswordForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']

            user = (Customer.objects.filter(user__username = identifier).first() or
                    Customer.objects.filter(user__email = identifier).first())

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

                request.session['password-reset-user-id'] = user.user.id   #ذخیره ایدی کاربر در سشنه کاربر.
                messages.success(request, 'Token has been sent to your email.')
                return redirect('customer-verify-password-token')

            else:
                messages.error(request, 'User not found.')

    return render(request, 'customer/forgot_password.html', {'form': form})



def VerifyForgotPasswordTokenView(request):
    if request.method == 'POST':
        token_input = request.POST.get('token')
        user_id = request.session.get('password-reset-user-id')     #برداشتن ایدی کاربر از سشن.

        if not user_id:
            messages.error(request, 'Session expired. Please request a new code.')
            return redirect('customer-forgot-password')

        cache_key = f'password-reset-token-{user_id}'
        cache_token = cache.get(cache_key)

        if not cache_token:
            messages.error(request, 'Token has expired. Please request a new one.')
            return redirect('customer-forgot-password')

        if int(token_input) == cache_token:
            return redirect('customer-reset-password')

        else:
            messages.error(request, 'Invalid token.Please try again.')

    return render(request, 'customer/verify_password_token.html')



def ResetPasswordView(request):
    form = CustomerResetPasswordForm()

    if request.method == 'POST':
        form = CustomerResetPasswordForm(request.POST)
        if form.is_valid():
            user_id = request.session.get('password-reset-user-id')

            if not user_id:
                messages.error(request, 'Session expired. Please request a new code.')
                return redirect('customer-forgot-password')

            user = Customer.objects.get(user__id=user_id)

            if user:
                new_password = form.cleaned_data['new_password']
                user.user.set_password(new_password)
                user.user.save()

                cache.delete(f'password-reset-token-{user_id}')
                del request.session['password-reset-user-id']

                messages.success(request, 'Your password has been reset.You can now log in.')
                return redirect('customer-login')

            else:
                messages.error(request, 'User not found.')
                return redirect('customer-forgot-password')

    return render(request, 'customer/reset_password.html', {'form': form})




@login_required()
def CustomerDashboardView(request):
    return render(request, 'customer/dashboard.html')




@login_required()
def CustomerProfileView(request):
    user = request.user

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance = user)
        if form.is_valid():
            if request.POST.get('remove_image') == 'on' and user.image:
                user.image.delete(save = False)
                user.image = None
                user.save()

            phone = form.cleaned_data['phone']
            if len(phone) != 11:
                messages.error(request, 'The number must be 11 digits.')

            else:
                form.save()
                messages.success(request, 'Profile updated successfully.')
                return redirect('customer-profile')

        else:
            messages.error(request, 'Please correct the errors below.')

    else:
        form = CustomerProfileForm(instance=user)
    return render(request, 'customer/profile.html', {'form': form})




@login_required()
def CustomerOrderView(request):
    user = request.user
    order_items = OrderItem.objects.select_related('product', 'order', 'order__user').filter(
        order__user = user).order_by('-order__created_at')
    if request.method == 'POST':
        if 'delete_order' in request.POST:
            order_item_id = request.POST.get('order_item_id')
            order_item = get_object_or_404(OrderItem, id = order_item_id)
            order = order_item.order
            if order_item.order.user == user and order.is_paid == False:
                order.delete()

    return render(request, 'customer/order.html', context={'order': order_items})





def simulate_payment_page(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if request.method == "POST":
        order.is_paid = True
        order.save()
        return redirect('customer-orders')

    return render(request, 'payment/simulate_payment.html', {'order': order})

@login_required
def PaymentPage(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id, order__user=request.user)

    if order.order.is_paid:
        messages.info(request, "This order is already paid.")
        return redirect('customer-orders')

    return render(request, 'payment/payment_page.html', {'order': order})


@login_required
def PaymentSuccess(request, order_id):
    order_item = get_object_or_404(OrderItem, id=order_id, order__user=request.user)

    if not order_item.order.is_paid:
        order_item.order.is_paid = True
        order_item.order.save()
        messages.success(request, "Payment was successful.")

    return render(request, 'payment/payment_success.html', {'order': order_item})





@login_required()
def CustomerReviewView(request):
    user = request.user
    paid_orders = Order.objects.filter(user = user, is_paid = True)
    paid_products = Product.objects.filter(order_items__order__in=paid_orders).distinct()    # پیدا کردن محصولاتی که پرداخت شدن.
    reviewed_products_ids = Review.objects.filter(user = user).values_list('product_id', flat=True)    # (برای لیسته ساده flat) محصولاتی که نظر براشون ثبت شده.
    unreviewed_products = paid_products.exclude(id__in = reviewed_products_ids)
    reviewed_products = paid_products.filter(id__in = reviewed_products_ids)

    form = CustomerReviewForm()
    if request.method == 'POST':
        form = CustomerReviewForm(request.POST)
        product_id = request.POST.get('product_id')
        product = Product.objects.get(id = product_id)
        if form.is_valid():
            review = form.save(commit = False)
            review.user = user
            review.product = product
            review.save()
            messages.success(request, 'Review was successful.')
            return redirect('customer-review')

        else:
            messages.error(request, "Review wasn't successful.")

    return render(request, 'customer/review.html', {'form': form,
                                                                         'reviewed_products': reviewed_products,
                                                                         'unreviewed_products': unreviewed_products,})




@login_required()
def OrderRegistration(request):
    user = request.user
    product_id = request.POST.get('product_id')
    product = Product.objects.get(id = product_id)
    quantity = int(request.POST.get('quantity'))

    if user:
        order= Order.objects.create(user = user , is_paid = False)

        OrderItem.objects.get_or_create(
            order=order,
            product=product,
            quantity=quantity,
            unit_price=product.price,
            status='pending'
        )

        return redirect('global-home')




@login_required()
def CustomerLogoutView(request):
    logout(request)
    return redirect('global-home')

