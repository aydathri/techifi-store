from django.urls import path
from store.views.home_view import (GlobalHome, ProductDtailView)
from store.views.customer_view import (SignUpView, VerifyTokenView, LoginView, ForgotPasswordView,
                                       VerifyForgotPasswordTokenView, ResetPasswordView, CustomerDashboardView,
                                       CustomerProfileView, CustomerOrderView,PaymentPage, PaymentSuccess,simulate_payment_page,
                                       CustomerReviewView, OrderRegistration, CustomerLogoutView)

from store.views.manager_view import (ManagerSingUpView, ManagerVerifyTokenView, ManagerLoginView,
                                      ManagerForgotPasswordView, ManagerVerifyForgotPasswordTokenView,
                                      ManagerResetPasswordView, ManagerDashboarView, ManagerEditProfileView,
                                      ManagerShowCustomersView, ManagerCustomerDelete, CategoryView,
                                      ProductView, ReviewView, OrderView, LogoutView)

urlpatterns = [
    path('', GlobalHome, name='global-home'),
    path('product-detail', ProductDtailView, name='product-detail'),

    ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###

    path('customer-sign-up/', SignUpView, name='customer-sign-up'),
    path('customer-verifi-token/', VerifyTokenView, name='customer-verify-login-token'),
    path('customer-login/', LoginView, name='customer-login'),
    path('customer-forgot-password/', ForgotPasswordView, name='customer-forgot-password'),
    path('customer-verify-password-token/', VerifyForgotPasswordTokenView, name='customer-verify-password-token'),
    path('customer-reset-password/', ResetPasswordView, name='customer-reset-password'),
    path('customer-dashboard/', CustomerDashboardView, name='customer-dashboard'),
    path('customer-profile/', CustomerProfileView, name='customer-profile'),
    path('customer-order/', CustomerOrderView, name='customer-orders'),


    path('payment/<int:order_id>/', PaymentPage, name='payment_page'),
    path('payment/<int:order_id>/simulate/', simulate_payment_page, name='simulate_payment_page'),
    path('payment/<int:order_id>/success/', PaymentSuccess, name='payment_success'),

    path('customer-review/', CustomerReviewView, name='customer-review'),
    path('order-registration/', OrderRegistration, name='order-registration'),

    path('customer-logout/', CustomerLogoutView, name='customer-logout'),

    ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###  ###

    path('manager-sign-up/', ManagerSingUpView, name='manager-sign-up'),
    path('manager-verifi-token/', ManagerVerifyTokenView, name='manager-verify-login-token'),
    path('manager-login/', ManagerLoginView, name='manager-login'),
    path('manager-forgot-password/', ManagerForgotPasswordView, name='manager-forgot-password'),
    path('manager-verify-password-token/', ManagerVerifyForgotPasswordTokenView, name='manager-verify-password-token'),
    path('manager-reset-password/', ManagerResetPasswordView, name='manager-reset-password'),
    path('manager-dashboard', ManagerDashboarView, name='manager-dashboard'),
    path('manager-profile', ManagerEditProfileView, name='manager-profile'),
    path('manager-show-customer', ManagerShowCustomersView, name='manager-show-customer'),
    path('customers/delete/<int:customer_id>/', ManagerCustomerDelete, name='delete-customer'),
    path('categories/', CategoryView, name='manage-categories'),
    path('products/', ProductView, name='manage-products'),
    path('reviews/', ReviewView, name='manage-reviews'),
    path('orders/', OrderView, name='manager-orders'),
    path('manager-logout/', LogoutView, name='manager-logout'),
]


# ذخیره فایل
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
