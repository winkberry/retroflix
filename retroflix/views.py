from django.shortcuts import render

# Create your views here.
def landing(request):
    if request.method =="GET":
        return render(request,'landing.html')

def main(request):
    if request.method =="GET":
        return render(request,'main/main.html')

# def detail(request):
#     if request method =="GET":
#         return render(request, 'detail/detail.html')