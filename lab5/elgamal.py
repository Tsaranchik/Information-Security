from prime_generator import PrimeGenerator
import random
import math


class ElGamal:
	def __init__(self) -> None:
		...
	
	def generate_keys(self, bits=128):
		p = PrimeGenerator.generate_large_prime(bits)
		g = 2

		x = random.randint(2, p - 2)
		y = pow(g, x, p)

		public_key = {'p': p, 'g': g, 'y': y}
		private_key = {'p': p, 'x': x}

		return public_key, private_key
	
	def _encrypt(self, message, public_key: dict) -> tuple:
		p = public_key['p']
		g = public_key['g']
		y = public_key['y']

		if isinstance(message, str):
			m = int.from_bytes(message.encode('utf-8'), 'big')
		else:
			m = message
		
		m = m % p

		while True:
			k = random.randint(2, p - 2)
			if math.gcd(k, p - 1) == 1:
				break
		
		a = pow(g, k, p)
		b = (pow(y, k, p) * (m % p)) % p

		return a, b
	
	def _decrypt(self, a: int, b: int, private_key: dict) -> int:
		p = private_key['p']
		x = private_key['x']
		ax = pow(a, x, p)
		ax_inv = pow(ax, -1, p)
		m = (b * ax_inv) % p

		return m
	
	def encrypt_file(self, input_file: str, output_file: str, public_key: dict) -> bool:
		try:
			with open(input_file, 'rb') as f:
				data = f.read()
			
			encrypted_data = []
			for byte in data:
				a, b = self._encrypt(byte, public_key)
				encrypted_data.extend([a, b])
			
			with open(output_file, 'w') as f:
				for i in range(0, len(encrypted_data), 2):
					f.write(f"{encrypted_data[i]},{encrypted_data[i+1]}\n")
			
			return True
		except Exception as e:
			print(f"Ошибка при шифровании файла: {e}")
			return False
	
	def decrypt_file(self, input_file: str, output_file: str, private_key: dict) -> bool:
		try:
			with open(input_file, 'r') as f:
				lines = f.readlines()
			
			decrypted_data = bytearray()
			
			for line in lines:
				a_str, b_str = line.strip().split(",")
				a = int(a_str)
				b = int(b_str)

				byte_val = self._decrypt(a, b, private_key)
				decrypted_data.append(byte_val)
			
			with open(output_file, 'wb') as f:
				f.write(decrypted_data)
			
			return True
		except Exception as e:
			print(f"Ошибка при дешифровании файла: {e}")
			return False
