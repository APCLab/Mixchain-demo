from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import *

# Create your views here.
def index(req):
    return render(req, 'index.html')

def hello(req):
    return render(req, 'hello.html')

def login(req):
    print("test")
    if req.method == 'POST':
        user_id = req.POST['user_id']
        print (user_id)
        token_id = req.POST['token_id']
        print (token_id)
        tar_user = Tokens.objects.get(user=user_id,token=token_id)
        return render(req, 'hello.html',{'token_id':token_id})
    else:
        print("GET")
        return render(req, 'login.html')


def auth(req):
    if req.method == 'GET':
        return render(req, 'auth.html')
    
    # get or create user
    us, _ = User.objects.get_or_create(address = req.POST['user_id'],pub_key=req.POST['key_id']) 
   #us.pub_key = req.POST['key_id']
   # us.save()

    # get auth
    """
    au, _ = authority.objects.get_or_create(address = us, chain = req.POST['chain'])
    au.read = ('read' in req.POST['read'])
    au.write = ('write' in req.POST['write'])
    au.save()
"""
    # get token
    tkn, _ = Tokens.objects.get_or_create(user = us, chain = req.POST['chain'])
    tkn.read = 'read' in req.POST
    tkn.write = 'write' in req.POST
    tkn.save()   
 
    return render(req, 'auth.html', {'token' : tkn})
