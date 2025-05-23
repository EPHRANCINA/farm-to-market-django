from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.http import JsonResponse

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/', include('auth_app.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('orders.urls')),
    path('api/messages/', include('messages.urls')),
    path('api/reviews/', include('reviews.urls')),
    path('api/health/', lambda request: JsonResponse({'status': 'healthy', 'message': 'API is running'}), name='health_check'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 