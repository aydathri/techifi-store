from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from store.models import OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def PaymentPage(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id, user=request.user)

    if order.order.is_paid:
        messages.info(request, "This order is already paid.")
        return redirect('customer-orders')

    return render(request, 'payment/payment_page.html', {'order': order})


@login_required
def PaymentSuccess(request, order_id):
    order = get_object_or_404(OrderItem, id=order_id, user=request.user)

    if not order.is_paid:
        order.is_paid = True
        order.save()
        messages.success(request, "Payment was successful.")

    return render(request, 'payment/payment_success.html', {'order': order})
