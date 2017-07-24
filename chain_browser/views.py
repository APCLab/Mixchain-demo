import json
import logging

from binascii import unhexlify

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from bitcoin.rpc import Proxy

import pyelliptic

from datetime import date
import time 
import datetime
from my_auth.models import *

def index(request):
    return render(request, 'index.jade')


def blockinfo(request):
    '''
    Accept ``GET`` parameters:

        - since
    '''
    block_idx = bitcoin_rpc('getblockcount')

    try:
        block_start = int(request.GET.get('since', -21))
    except ValueError:
        block_start = -21

    payload = {
        'blockcount': block_idx,
        'blocks': [
            bitcoin_rpc('getblock', bitcoin_rpc('getblockhash', block_idx - i))
            for i in range(min(
                21,
                block_idx + 1,
                block_idx - block_start))
        ],
    }
    return JsonResponse(payload)


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


def getblock(request, block_id):
    block_id = int(block_id)
    block = bitcoin_rpc('getblock', bitcoin_rpc('getblockhash', block_id))
    if not block:
        return JsonResponse({
            'state': 'error',
        })
    return JsonResponse(block)


def gettx(request, tx_id):
    tx = bitcoin_rpc('gettransaction', tx_id)
    if not tx:
        return JsonResponse({
            'state': 'error',
        })

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
            
            
            #op_returns.append(json.loads(unhexlify(code).decode()))
            if 'chain' in request.session:
                chain= request.session['chain']
                read = request.session['read']
                write= request.session['write']
                
            
            try:
                if a['Type']=='bid':
                    request.session['exp_date']=a['Expiration_date']
                    today=date.today()
                    exp=datetime.datetime.strptime(a['Expiration_date'], "%Y-%m-%d").date()
                    pi=Bid.objects.get(txid=tx_id)
                    c1=pyelliptic.ECC(pubkey=bytes.fromhex(pi.pub_key1),privkey=bytes.fromhex(pi.pri_key1),curve="secp256k1")
                    c2=pyelliptic.ECC(pubkey=bytes.fromhex(pi.pub_key2),privkey=bytes.fromhex(pi.pri_key2),curve="secp256k1")
                    if a['Chain']==str(chain):
                        if exp < today:
                            r=bytes.fromhex(a['Real_price'])
                            p=bytes.fromhex(a['Start_price'])
                            de_sp=c1.decrypt(p).decode("utf-8")
                            de_rp=c2.decrypt(r).decode("utf-8")
                            op_returns.append({"Channel":a['Chain'],"Type":a['Type'],"Expiration_date":a['Expiration_date'],"Start_price":'$'+de_sp,"Real_price":'$'+de_rp})
                            
                        else:
                            p=bytes.fromhex(a['Start_price'])
                            de_sp=c1.decrypt(p).decode("utf-8")
                            op_returns.append({"Channel":a['Chain'],"Type":a['Type'],"Expiration_date":a['Expiration_date'],"Start_price":'$'+de_sp,"Real_price":a['Real_price']})

                    else:
                        op_returns.append({"Channel":a['Chain'],"Type":a['Type'],"Expiration_date":a['Expiration_date'],"Start_price":a['Start_price'],"Real_price":a['Real_price']})
                      
                elif a['Type']=='bid_price':
                    number=request.session['number']
                    print(number)
                    ai=Bid.objects.get(number = number)
                    a1=pyelliptic.ECC(pubkey=bytes.fromhex(ai.pub_key1),privkey=bytes.fromhex(ai.pri_key1),curve="secp256k1")
                    a2=pyelliptic.ECC(pubkey=bytes.fromhex(ai.pub_key2),privkey=bytes.fromhex(ai.pri_key2),curve="secp256k1")
                    p1=bytes.fromhex(a['Price'])
                    de_data=a1.decrypt(p1).decode("utf-8")
                    p2=bytes.fromhex(a['User'])
                    de_usr=a2.decrypt(p2).decode("utf-8")
                    now = datetime.datetime.today()
                    ti= int(time.mktime(now.timetuple()))
                    if a['Chain']==str(chain):
                        if read == 'yes' or True:
                            if ai.exp_time<ti:
                                op_returns.append({"Channel":a['Chain'],"Type":a['Type'],"Price":'$'+de_data,"User":de_usr})
                            else:
                                op_returns.append({"Channel":a['Chain'],"Type":a['Type'],"Price":'$'+de_data,"User":a['User']})
                            
                        else:

                            op_returns.append({"message":"Permission denied","type":"read error"})
                    else:
                        op_returns.append({"message":"Permission denied","type":"channel error"})
                   
                elif a['Type']=='Auth':
                    #op_returns.append(json.loads(unhexlify(code).decode()))
                    op_returns.append({"Type":a['Type'],"ID":a['ID'],"Channel":a['Chain'],"Password":a['Password'],"Send_bid":a["Send_bid"],"Read":a['Read'],"Write":a['Write'],"Exp_date":a['Exp_date']})
            except:
                op_returns.append({"message":"permission error","type":"except error"})
            #if a['chain'] == '6':
            #    op_returns.append({'lab':'APC'})
            #else:
            #    op_returns.append(json.loads(unhexlify(code).decode()))
    return JsonResponse({
        'tx': tx,
        'op_returns': op_returns,
    })
