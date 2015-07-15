from django.shortcuts import render


def home(request):
    return render(request, 'main/main.html')


def credit(request):
    return render(request, 'main/credit.html')
