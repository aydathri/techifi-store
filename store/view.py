from django.core.mail import send_mail
from django.http import HttpResponse

def test_email(request):
    send_mail(
        'سلام از طرف آیدا 🎉',
        'این یک ایمیل تستی هست که با Brevo فرستاده شده.',
        '9317eb001@smtp-brevo.com',  # فرستنده
        ['aidat3991@gmail.com'],        # گیرنده
        fail_silently=False,
    )
    return HttpResponse('ایمیل فرستاده شد ✅')
