from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('testimonial/', views.testimonial, name='testimonial'),
    path('contact/', views.contact, name='contact'),
    path('product/', views.watch_list, name='product'),
    
    path('login/', views.login_view, name='login'),
    path('signup/', views.register, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('place-order/<int:watch_id>/', views.place_order, name='place_order'),
    path('order_success/', views.order_success, name= 'order_success'),
    path('my-orders/', views.user_orders, name='user_orders'),
    path('submit-testimonial/', views.submit_testimonial, name='submit_testimonial'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('change-password/', auth_views.PasswordChangeView.as_view(template_name='change_password.html', success_url='/my-profile/'), name='change_password'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:watch_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-quantity/<int:item_id>/', views.update_quantity, name='update_quantity'),
    path('place-cart-order/', views.place_cart_order, name='place_cart_order'),

]
