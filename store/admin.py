from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Customer, Manager, EmailToken, Category, Product, Order, OrderItem, Review
# 123456dj


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'phone', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone')
    ordering = ('-date_joined',)
    list_filter = ('is_active', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'phone', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'avatar', 'address')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')

@admin.register(EmailToken)
class EmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token', 'created_at')
    search_fields = ('user__username', 'token')
    readonly_fields = ('created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price', 'is_active','id')
    list_filter = ('category', 'is_active')
    search_fields = ('title', 'description')
    list_editable = ('is_active',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'is_paid', 'created_at', 'total_price_display']
    list_filter = ['is_paid', 'created_at']
    search_fields = ['user__username', 'user__email']

    def total_price_display(self, obj):
        return f'{sum(item.total_price for item in obj.items.all()):,.2f}'
    total_price_display.short_description = 'Total Price'

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id','order', 'product', 'quantity', 'unit_price', 'status', 'total_price']
    list_filter = ['status']
    search_fields = ['product__title', 'order__user__username']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'score', 'created_at', 'short_description')
    list_filter = ('score', 'created_at')
    search_fields = ('user__username', 'product__title', 'description')
    autocomplete_fields = ['user', 'product']
    readonly_fields = ['created_at']

    def short_description(self, obj):
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description

    short_description.short_description = 'Description'