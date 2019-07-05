from django.shortcuts import render, HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("For Restrited People. If you Dont have authorization, do not enter here!")