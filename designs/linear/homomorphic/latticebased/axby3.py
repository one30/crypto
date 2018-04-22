from collections import namedtuple
from math import log, ceil

from crypto.utilities import random_integer, modular_inverse, gcd, secret_split, dot_product

SECURITY_LEVEL = 32

Key_Tuple = namedtuple("key", ["encryption_key", "decryption_key"])

def generate_parameters(security_level=SECURITY_LEVEL):
    parameters = dict()
    parameters["inverse_size"] = inverse_size = security_level
    parameters["x_size"] = x_size = security_level * 3
    
    parameters["q_size"] = q_size = (((inverse_size * 2) + x_size + 1) * 8)
    
    parameters["dimensions"] = dimensions = q_size / security_level
    parameters["r_size"] = security_level
    parameters["inverse_shift"] = (security_level * 8) + int(ceil(log(dimensions, 2))) # second term adds headroom for additions
    parameters["lsb_mask"] = (2 ** (security_level * 8)) - 1
    parameters["x_modulus"] = 2 ** (x_size * 8)
    return parameters
    
PARAMETERS = generate_parameters(SECURITY_LEVEL)
    
def find_q(parameters=PARAMETERS):
    from crypto.utilities import is_prime
    q_size = parameters["q_size"]
    offset = 1
    q_base = (2 ** q_size)
    while not is_prime(q_base + offset):
        offset += 2
    return q_base, offset
    
#Q_BASE, OFFSET = find_q(PARAMETERS)    
#print OFFSET
#Q = Q_BASE + OFFSET
Q = (2 ** PARAMETERS["q_size"]) + 445

def generate_secret_key(parameters=PARAMETERS, q=Q):
    inverse_size = parameters["inverse_size"]
    inverse_shift = parameters["inverse_shift"]
    ai = (random_integer(inverse_size) << inverse_shift) + 1
    bi = (random_integer(inverse_size) << inverse_shift) + 1    
    d = (ai * bi) % q
    a = modular_inverse(ai, q)
    b = modular_inverse(bi, q)        
    return Key_Tuple((a, b), d)
        
def encrypt(m, key, parameters=PARAMETERS, q=Q):           
    message_vector = secret_split(m, parameters["x_size"], 2, parameters["x_modulus"])            
    ciphertext = dot_product(key.encryption_key, message_vector) % q    
    return ciphertext
    
def decrypt(ciphertext, key, parameters=PARAMETERS, q=Q):    
    return ((ciphertext * key.decryption_key) % q) & parameters["lsb_mask"]
    
def test_encrypt_decrypt():
    key = generate_secret_key()
    m0 = 0
    m1 = 1
    mr = random_integer(SECURITY_LEVEL)
    
    c0 = encrypt(m0, key)
    c1 = encrypt(m1, key)
    cr = encrypt(mr, key)
    
    p0 = decrypt(c0, key)
    p1 = decrypt(c1, key)
    pr = decrypt(cr, key)
    
    assert (m0 == p0), (m0, p0)
    assert (m1 == p1), (m1, p1)
    assert (mr == pr), (mr, pr)
    
    from unittesting import test_symmetric_encrypt_decrypt
    test_symmetric_encrypt_decrypt("axby3", generate_secret_key, encrypt, decrypt, iterations=10000)
    
if __name__ == "__main__":
    test_encrypt_decrypt()
    