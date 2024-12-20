from django.urls import path
from . import views, utilitiesViews
from graph import views as graph



urlpatterns = [
	path('', views.home, name='home'),
	path('loadForm/', views.loadForm, name='ajax_load'),
    path('infoGenerated/', views.loadData, name='infoGenerated'),
	path('carinfo/<int:pk>/',views.carPage, name='carPage'),
	path('gallery',views.gallery, name='gallery'),


	path('register/', views.registerPage, name='register'),
	path('logout/',views.logoutPage, name='logout'),
	path('customer/<pk>/',views.customerPage, name='customer'),
	path('updateView/',views.updateView, name='updateView'),
	


	path('createOrder/<int:pk>/',views.createOrder, name='createOrder'),
	path('makeOrder/<int:pk>/',views.makeOrder, name='makeOrder'),
	path('payment/<int:pk>/', views.payment, name='payment'),
	path('cancelOrder/<int:pk>/', views.cancelOrder, name='cancelOrder'),


	path('pdfView/<int:pk>/', utilitiesViews.ViewPDF.as_view(), name="pdfView"),
    path('pdfDownload/<int:pk>/', utilitiesViews.DownloadPDF.as_view(), name="pdfDownload"),
	
	path('graph', graph.graph, name="graph"),

]
