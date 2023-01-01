import random
from math import gcd

#判断是不是质数
def prime(num):
    if num>1:
        s=0
        for i in range(1,num):
            if num%i==0:
                s+=1
        if s==1:
            return True
    return False

#随机获得p和q 从而得到n
def get_primes():
    p=0
    q=0
    while not(prime(p) and prime(q) and p!=q):
        p=random.randint(23,200)
        q=random.randint(23,200)
    return p,q,

def get_n(p,q):
    n=p*q
    return n

#根据那个公式 得到phi的值
def get_phi(p,q):
    phi=(p-1)*(q-1)
    return phi

#分解成可以被除掉的数
def get_primefactors(n): 
    fac_list=[]
    for i in range(1,n+1):
        if n%i==0:
            fac_list.append(i)
    return fac_list


def get_coprimes(n,factors):
    coprimes=[]
    for i in factors:
        if gcd(n,i) == 1:
            coprimes.append(i)
    return coprimes



#得到奇数e e是公共密钥  并且不是fac_list中的数
def  get_e(n,phi):
    phi_factors=get_primefactors(phi)
    n_fac=get_primefactors(n)
    n_fac.extend(phi_factors)
    factors=set(n_fac)
    s=[]
    for i in range(2,(phi+1)):
        lst=get_coprimes(i,factors)
        s.extend(lst)
    e=random.choice(s)
    return e



#得到私钥d 用模式算法
def get_d(e,phi):
    lst=[]
    for d in range(3,phi):
        if ((d*e)%phi)==1:
            lst.append(d)
    if lst==[]:
        return None
    d=random.choice(lst)
    return d


#得到公钥e,n 私钥d,n
def generate_keys():
    d=None
    while d is None:
        p,q =get_primes()
        n=get_n(p,q)
        phi=get_phi(p,q)
        e=get_e(n,phi)
        d=get_d(e,phi)
    return (e,n),(d,n)



#加密
def encrypt(msg,key):
    encrypted=''
    for i in msg:
        s=(ord(i)**key[0])%key[1]
        encrypted+=chr(s)
    return encrypted



#解密
def decrypt(pri_key,l_text):
    d,n=pri_key
    o_text=''
    for i in l_text:
        o_text+= chr(ord(i)**d%n)
    return o_text





