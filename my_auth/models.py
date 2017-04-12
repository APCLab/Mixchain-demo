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
