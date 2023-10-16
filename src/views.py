from django.shortcuts import render
from src.app_dash import cities
# Create your views here.
def view_immo(request):
        return render(request,"immo_app.html")

