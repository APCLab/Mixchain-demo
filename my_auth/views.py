from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from .models import *
from OP_RETURN import *
from django.http import HttpResponse,Http404
from django.template.loader import get_template
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import JsonResponse
from django.conf import settings
from django.db.models import Count
from datetime import datetime,time,date
from django.template import loader
import time
import datetime

import json
import pyelliptic

import json
import logging

from binascii import unhexlify
from bitcoin.rpc import Proxy
def gettx(tx_id):
    tx = bitcoin_rpc('gettransaction', tx_id)
    if not tx:
        return JsonResponse({
            'state': 'error',
        })

    raw = tx.get('hex')
    op = []
    if raw:
        decode = tx['decode'] = bitcoin_rpc('decoderawtransaction', raw)

        for out in decode.get('vout'):
            script = out.get('scriptPubKey')
            if not script:
                continue

            type_ = script.get('type')
            if type_ != 'nulldata':
                continue

            asm = script.get('asm')
            if not asm.startswith('OP_RETURN'):
                continue
            code = asm.split()[-1]
            tt=json.loads(unhexlify(code).decode())
            op.append(json.loads(unhexlify(code).decode()))
    return op


# Create your views here.
def logout(req):
    req.session.flush()
    response=redirect('/login')
    return response



def test(req):
    if 'exp_date' in req.session:

        exp = req.session['exp_date']    
    today=datetime.today()
    template = get_template('test.html')
    html= template.render(locals())
    return HttpResponse(html)

def index(req):
    return render(req, 'index.html')

def hello(req):
    try:
        if 'chain' in req.session:
            chain= req.session['chain']
            read = req.session['read']
            write= req.session['write']
            token= req.session['token']
    except:
        return redirect('/')     
    template = get_template('hello.html')
    html= template.render(locals())
    return HttpResponse(html)

def log(req):
    return render(req, 'login.html')
def bid(req):
    if req.method == 'GET':
        days=range(1,30)
        if 'chain' in req.session:
            chain= req.session['chain']
            read = req.session['read']
            write= req.session['write']
            user = req.session['uid']
            txid = req.session['tx_id']
            bid  = req.session['send_bid']
        
        if bid=='yes':
            a=1
        else:
            a=-1
        return render(req, 'bid.html',{'days':days,'chain':chain,'read':read,'write':write,'user':user,'txid':txid,'a':a})

def list(req):
    if 'chain' in req.session:
        chain= req.session['chain']
        read = req.session['read']
        write= req.session['write']
        user = req.session['uid']
        txid = req.session['tx_id']
        uid  = req.session['uid']    
    
   
    if read=='false':
        bid=Bid.objects.filter(chain=chain)
    
    else:
        bid = Bid.objects.all()
    now = datetime.datetime.today()
    exp1 = time.mktime(now.timetuple())
    exp = int(exp1)
    template = get_template('list.html')
    html = template.render(locals())
    return HttpResponse(html)

def listing(req,number):
    if req.method == 'GET':
        if 'chain' in req.session:
            chain= req.session['chain']
            read = req.session['read']
            write= req.session['write']
            user = req.session['uid']
            txid = req.session['tx_id']
            uid  = req.session['uid']

        try:
            view = list_Bid.objects.filter(number=number)
        except list_BidDoseNotExist:
            raise Http404('找不到標案編號')
     
        req.session['number']=number   
        template = get_template('listing.html')
        html = template.render(locals())
        return HttpResponse(html)
        #return render(req,'listing.html',{'view':view})

def settlement(req,number):
    if req.method == 'GET':
        req.session['number']=number
        chain= req.session['chain']
        read = req.session['read']
        write= req.session['write']
        user = req.session['uid']
        txid = req.session['tx_id']
        uid  = req.session['uid']

        dic={}
        view = list_Bid.objects.filter(number=number)
        pi = Bid.objects.get(number=number)
        c1=pyelliptic.ECC(pubkey=bytes.fromhex(pi.pub_key1),privkey=bytes.fromhex(pi.pri_key1),curve="secp256k1")
        
        c2=pyelliptic.ECC(pubkey=bytes.fromhex(pi.pub_key2),privkey=bytes.fromhex(pi.pri_key2),curve="secp256k1")
        for b in view:
            tx = bitcoin_rpc('gettransaction', b.list_id)
            if not tx:
                raise Http404('Token錯誤')
            raw = tx.get('hex')
            op_returns = []
            if raw:
                decode = tx['decode'] = bitcoin_rpc('decoderawtransaction', raw)

                for out in decode.get('vout'):
                    script = out.get('scriptPubKey')
                    if not script:
                        continue

                    type_ = script.get('type')
                    if type_ != 'nulldata':
                        continue

                    asm = script.get('asm')
                    if not asm.startswith('OP_RETURN'):
                        continue

                    code = asm.split()[-1]
                    a=json.loads(unhexlify(code).decode())
                    p1=bytes.fromhex(a['Price'])
                    de_data=int(c1.decrypt(p1).decode("utf-8"))
                    b={b.list_id:de_data}
                    dic.update(b)

        dict= sorted(dic.items(), key=lambda d:d[1], reverse = True)
        try:
            txid=dict[0][0]
            price=int(dict[0][1])
            test1=gettx(pi.txid)
            real=bytes.fromhex(test1[0]['Real_price'])
            r_price=int(c2.decrypt(real).decode("utf-8"))
            print(r_price)
        except:
            message = '無人投標 流標!'
        #print(test1[0]['Number'])
        
        template = get_template('settlement.html')
        html = template.render(locals())
        return HttpResponse(html)

            

def list_detail(req,number):
    return render(req,'disp.html')


def bidding(req,number):
    if 'chain' in req.session:
        chain= req.session['chain']
        read = req.session['read']
        write= req.session['write']
        user = req.session['uid']
        txid= req.session['tx_id']

    try:
        b = Bid.objects.get(number=number)
        c1=pyelliptic.ECC(pubkey=bytes.fromhex(b.pub_key1),privkey=bytes.fromhex(b.pri_key1),curve="secp256k1")
        start=gettx(b.txid)
        #print(start[0]['Start_price'])
        sp=bytes.fromhex(start[0]['Start_price'])
        #print(sp)
        s_price=int(c1.decrypt(sp).decode("utf-8"))
        req.session['number']=number
        if write=='yes':
            a=5
        else:
            a=3
    except:
        raise Http404('找不到標案編號')
    #template = get_template('price.html')
    #html= template.render(locals())
    #return HttpResponse(html)

    return render(req,'price.html',{'b':b,'user':user,'s_price':s_price,'chain':chain,'read':read,'write':write,'txid':txid,'a':a})

def old(req):
    if req.method == 'POST':
        user_id = req.POST['user_id']
        token_id = req.POST['token_id']
        tar_user = Tokens.objects.get(user=user_id,token=token_id)
        req.session['chain']=tar_user.chain
        req.session['read'] =tar_user.read
        req.session['write']=tar_user.write
        req.session['token'] =tar_user.token
        req.session['user'] =user_id
        return redirect('/hello')
        #return render(req, 'hello.html',{'tar_user':tar_user})
    else:
        print("GET")
        return render(req, 'login.html')

def bitcoin_rpc(*args, **kwargs):
    '''
    Wrapper of bitcoin.rpc
    '''
    try:
        rpc = Proxy(settings.BITCOIN_API)
        return rpc._call(*args, **kwargs)
    except Exception as err:
        logging.error(err)
        return False

def login(req):
    if req.method == 'POST':
        tx_id = req.POST['u_id']
        pwd  = req.POST['u_pw']
        tx = bitcoin_rpc('gettransaction', tx_id)
        if not tx:
            raise Http404('Token錯誤')
        raw = tx.get('hex')
        op_returns = []
        if raw:
            decode = tx['decode'] = bitcoin_rpc('decoderawtransaction', raw)

            for out in decode.get('vout'):
                script = out.get('scriptPubKey')
                if not script:
                    continue

                type_ = script.get('type')
                if type_ != 'nulldata':
                    continue

                asm = script.get('asm')
                if not asm.startswith('OP_RETURN'):
                    continue

                code = asm.split()[-1]
                a=json.loads(unhexlify(code).decode())
                
                try:
                    if a['Password']==str(pwd):
                        req.session['chain']=a['Chain']
                        req.session['read']=a['Read']
                        req.session['write']=a['Write']
                        req.session['exp_date']=a['Exp_date']
                        req.session['uid']=a['ID']
                        req.session['send_bid']=a['Send_bid']
                        req.session['tx_id']=tx_id
                        return redirect('/list')
                except:   
                    raise Http404('Token或密碼錯誤')
    else:
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

def re_auth(req):
    if req.method == 'GET':
        days=range(1,101)
        return render(req, 're_auth.html',{'days':days})
    
def send_bid(req):
    if req.method == 'GET':
        return render(req,'hello.html')
    if 'chain' in req.session:
        chain= req.session['chain']
        read = req.session['read']
        write= req.session['write']
        user = req.session['uid']
        txid = req.session['tx_id']
        uid  = req.session['uid']
    
    u = req.POST['user']
    c = req.POST['chain']
    #n = req.POST['number']
    n =''.join([random.choice(string.digits) for _ in range(4)])
    s = req.POST['start_price']
    r = req.POST['real_price']
    pro = req.POST['product']
    exp = req.POST['exp']
    days=range(1,30)

    curve = "secp256k1"
    key1= pyelliptic.ECC(curve=curve)
    key2 = pyelliptic.ECC(curve=curve)
    
    pubkey1=key1.get_pubkey().hex()
    prikey1=key1.get_privkey().hex()
    pubkey2=key2.get_pubkey().hex()
    prikey2=key2.get_privkey().hex()

    s2=key1.encrypt(s, key1.get_pubkey()).hex()
    r2=key2.encrypt(r, key2.get_pubkey()).hex()
    
    today=datetime.date.today()
   # exp_time = str(date(today.year,today.month,today.day+int(exp)))
    exp_time=str(datetime.date.today() + datetime.timedelta(days=int(exp)))


    message={"Type":"bid","User":u,"Chain":c,"Number":n,"Start_price":s2,"Real_price":r2,"Expiration_date":exp_time}
    me=json.dumps(message)
    result= OP_RETURN_store(me)
    re = result['txids'][0]
    #a=(date(today.year,today.month,today.day+int(exp)))
    #a=datetime.date.today() + datetime.timedelta(days=int(exp))
    aa=datetime.datetime.combine(datetime.date.today()+ datetime.timedelta(days=int(exp)), datetime.time.max)
    da=timestamp = time.mktime(aa.timetuple())
    bi,_ = Bid.objects.get_or_create(chain = c ,number = n,txid = re,pub_key1 = pubkey1,pri_key1 = prikey1,pub_key2 = pubkey2, pri_key2 = prikey2,exp_time = da,product = pro)
    bi.save()
    a=1
    template = get_template('bid.html')
    html= template.render(locals())
    return HttpResponse(html)
    #return render(req, 'bid.html',{'re':re})
#@csrf_exempt
def bid_price(req):
    if req.method =='GET':
        return render(req,'hello.html')
    if 'chain' in req.session:
        chain= req.session['chain']
        read = req.session['read']
        write= req.session['write']
        user = req.session['uid']
        txid= req.session['tx_id']
   
    c = req.POST['chain']
    n = req.POST['number']
    #n=''.join([random.choice(string.digits) for _ in range(4)])
    u = req.POST['user']
    b = req.POST['bid_txid']
    p = req.POST['price']
    
    k=Bid.objects.get(txid=b)
    key1=k.pub_key1
    key2=k.pub_key2
    
    pk1=pyelliptic.ECC(pubkey=bytes.fromhex(k.pub_key1),privkey=bytes.fromhex(k.pri_key1),curve="secp256k1")
    pk2=pyelliptic.ECC(pubkey=bytes.fromhex(k.pub_key2),privkey=bytes.fromhex(k.pri_key2),curve="secp256k1")

    
    uk=pk2.encrypt(u, pk2.get_pubkey()).hex()
    pp=pk1.encrypt(p, pk1.get_pubkey()).hex()
    

    message={"Type":"bid_price","Chain":c,"Number":n,"User":uk,"Price":pp}
    me=json.dumps(message)
    result= OP_RETURN_store(me)
    be = result['txids'][0]
    ls= Bid.objects.get(txid=b,number=n)
    #pi,_ = list_Bid.objects.get_or_create(list_id = be,number=n,price=p,bid_itxid=ls.txid)
    pi = list_Bid.objects.create(list_id = be,number=n,price=p,bid_txid=ls)
    pi.save()
    a=4
    template = get_template('price.html')
    html= template.render(locals())
    return HttpResponse(html)
    #return render(req,'price.html',{'be':be})

def send_auth(req):
    if req.method=='GET':
        return render(req,'re_auth.html')
    
    uid = req.POST['user_id']
    upw = req.POST['user_pwd']
    uch = req.POST['user_chain']
    u_bi  = req.POST.getlist('send_bid')
    u_re  = req.POST.getlist('read')
    u_wr  = req.POST.getlist('write')
    u_da  = req.POST['exp']
    if not u_bi:
       aa='false'
    else:
       aa='yes'
    if not u_re:
       re='false'
    else:
       re='yes'
    if not u_wr:
       wr='false'
    else:
       wr='yes'
    days=range(1,101)
    a=str(datetime.date.today() + datetime.timedelta(days=int(u_da)))

    message={"Type":"Auth","ID":uid,"Password":upw,"Chain":uch,"Send_bid":aa,'Read':re,'Write':wr,'Exp_date':a}
    me=json.dumps(message)
    result= OP_RETURN_store(me)
    be = result['txids'][0]
    return render(req, 're_auth.html',{'days':days,'txid':be})
