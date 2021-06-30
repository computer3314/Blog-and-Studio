from django.shortcuts import render

# Create your views here.
# Create your views here.
def hello_view(request):
    return render(request, 'index.html', {
        'data': "Hello Django1 ",
    })