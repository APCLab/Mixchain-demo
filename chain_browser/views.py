import json
import logging

from binascii import unhexlify

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render

from bitcoin.rpc import Proxy


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
            op_returns.append(json.loads(unhexlify(code).decode()))

    return JsonResponse({
        'tx': tx,
        'op_returns': op_returns,
    })
