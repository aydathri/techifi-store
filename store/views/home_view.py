from store.models import Category, Product, Review
from django.shortcuts import render, get_object_or_404


def GlobalHome(request):
    search_query = request.GET.get('search_query', '')

    products = Product.objects.filter(is_active = True)
    categories = Category.objects.all()

    if search_query:
        products = products.filter(title__icontains = search_query)

    selected_category_title = request.GET.get('category')
    selected_category = None
    if selected_category_title:
        selected_category = Category.objects.filter(title = selected_category_title).first()
        if selected_category:
            products = products.filter(category=selected_category)

    return render(request, 'home/global_home.html', {'categories': categories,
                                                                         'products': products,
                                                                         'search_query': search_query,
                                                                         'selected_category': selected_category})




def ProductDtailView(request):
    product_title = request.GET.get('title')
    product = get_object_or_404(Product, title = product_title)
    reviews = Review.objects.filter(product = product)

    return render(request, 'home/product_detail.html', {'product': product,
                                                                            'reviews': reviews,})



