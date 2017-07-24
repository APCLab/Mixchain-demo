from django.db import models
import random
import string

# Create your models here.

def randstr():
    return ''.join([random.choice(string.digits) for _ in range(16)])

class User(models.Model):
    address = models.CharField(max_length=64, primary_key=True)
    pub_key = models.CharField(max_length=256)
    def __str__(self):
        return '%s %s' % (self.address,self.pub_key)
    
class Tokens(models.Model):
    user = models.ForeignKey(User)
    chain = models.SmallIntegerField()
    
    read = models.NullBooleanField()
    write = models.NullBooleanField()
    
    token = models.CharField(max_length = 32, default = randstr)
    
    def __str__(self):
        return '%s %s %s %s %s' % (self.user,self.token,self.chain,self.read,self.write)

class Bid(models.Model):
    chain = models.CharField(max_length =10,default=None,blank=True,null=True)
    number = models.CharField(max_length =10)
    txid = models.CharField(max_length =80, primary_key=True)
    pub_key1 = models.CharField(max_length =180,default=None,blank=True,null=True)
    pri_key1 = models.CharField(max_length =80,default=None,blank=True,null=True)
    pub_key2 = models.CharField(max_length =180,default=None,blank=True,null=True)
    pri_key2 = models.CharField(max_length =80,default=None,blank=True,null=True)
    exp_time = models.IntegerField(default=None,blank=True,null=True)
    product = models.CharField(max_length =100,default=None,blank=True,null=True)
    def __str__(self):
        return '%s %s %s %s %s %s %s %s' % (self.number,self.txid,self.chain,self.pub_key1,self.pri_key1,self.pub_key2,self.pri_key2,self.exp_time)

class list_Bid(models.Model):
    list_id = models.CharField(max_length =80, primary_key=True)
    number = models.CharField(max_length =10)
    price = models.CharField(max_length =10)
    bid_txid=models.ForeignKey(Bid)
    def __str__(self):
        return '%s %s %s %s' % (self.list_id,self.number,self.price,self.bid_txid)
