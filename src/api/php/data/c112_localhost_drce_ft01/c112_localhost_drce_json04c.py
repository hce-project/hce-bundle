import sys
import math
from decimal import *

def bbp(n):
    pi = Decimal(0)
    k = 0
    while k < n:
        pi += (Decimal(1)/(16**k))*((Decimal(4)/(8*k+1))-(Decimal(2)/(8*k+4))-(Decimal(1)/(8*k+5))-(Decimal(1)/(8*k+6)))
        k += 1
    return pi

def main(argv):

        if len(argv) != 2:
		sys.exit('Usage: BaileyBorweinPlouffe.py <prec> <n>')
		
	getcontext().prec = (int(sys.argv[1]))
	my_pi = bbp(int(sys.argv[2]))
	accuracy = 100*(Decimal(math.pi)-my_pi)/my_pi

	print "Pi is approximately " + str(my_pi)
	print "Accuracy with math.pi: " + str(accuracy)
    
if __name__ == "__main__":
	main(sys.argv[1:])
