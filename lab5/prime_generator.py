import random
import secrets


class PrimeGenerator:
	@staticmethod
	def test_miller_rabin(n: int, trials: int  = 5) -> bool:
		if n == 2 or n == 3:
			return True
		if n % 2 == 0 or n == 1:
			return False
		
		s = 0
		t = n - 1
		while t % 2 == 0:
			s += 1
			t //= 2
		
		for _ in range(trials):
			a = random.randint(2, n - 2)
			x = pow(a, t, n)

			if x == 1 or x == n - 1:
				continue

			for _ in range(s - 1):
				x = pow(x, 2, n)
				if x == n - 1:
					break
			else:
				return False
		
		return True
	
	@staticmethod
	def generate_large_prime(bits:int = 128) -> int:
		while True:
			candidate = secrets.randbits(bits)
			candidate |= (1 << (bits - 1)) | 1

			small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
			is_divisible = False
			for prime in small_primes:
				if candidate % prime == 0 and candidate != prime:
					is_divisible = True
					break
			if not is_divisible:
				if PrimeGenerator.test_miller_rabin(candidate):
					return candidate
