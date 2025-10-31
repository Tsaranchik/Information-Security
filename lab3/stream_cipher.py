import os
from typing import Callable
from generator import Generator
from hash_functions import HashFunctions
import hashlib

class StreamCipher:
	def __init__(self) -> None:
		self.generator = Generator()
		self.hash_func = HashFunctions()

	def encrypt_decrypt_file(
			self,
			input_file: str,
			output_file: str,
			password: str,
			hash_algorithm: str = 'ready',
			generator_type: str = 'yarrow-160'
	) -> bool:
		try:
			with open(input_file, 'rb') as f:
				data = f.read()
			key = self._generate_key_from_password(password, hash_algorithm)
			keystream = self._generate_keystream(len(data), key, generator_type, password)
			result = bytearray()
			
			for i, byte in enumerate(data):
				result.append(byte ^ keystream[i % len(keystream)])

			with open(output_file, 'wb') as f:
				f.write(bytes(result))
			
			return True
		
		except Exception as e:
			print(f"Ошибка при обработке файла: {e}")
			return False
	
	def _generate_key_from_password(self, password: str, hash_algorithm: str) -> bytes:
		password_bytes = password.encode('utf-8')

		if hash_algorithm == 'ready':
			hash_result = self.hash_func.ready_hash(password_bytes, 'sha256')
		elif hash_algorithm == 'ma_prime':
			hash_int = self.hash_func.ma_prime_hash(password_bytes)
			hash_result = hash_int.to_bytes(4, 'big')
		elif hash_algorithm == 'gost':
			hash_result = self.hash_func.gost_341194_hash(password_bytes)
		else:
			raise ValueError(f"Неизвестный алгоритм хеширования: {hash_algorithm}")

		return hash_result
	
	def _generate_keystream(self, length: int, key: bytes, generator_type: str, password: str) -> bytes:
		seed_data = password.encode() + key
		seed_int = int.from_bytes(hashlib.sha256(seed_data).digest()[:4], 'big')
		seed_bytes = hashlib.sha256(seed_data).digest()

		if generator_type == 'quadratic':
			bits = self.generator.quadratic_congruential_generator(length * 8, seed_int)
		elif generator_type == 'bbs':
			bits = self.generator.bbs_generator(length * 8, seed_int)
		elif generator_type == 'yarrow160':
			bits = self.generator.yarrow160_generator(length * 8, seed_bytes)
		else:
			raise ValueError(f"Неизвестный тип генератора: {generator_type}")

		keystream = self._bits_to_bytes(bits)

		return keystream[:length]
	
	def _bits_to_bytes(self, bits: list) -> bytes:
		bytes_list = []

		for i in range(0, len(bits), 8):
			byte = 0
			for j in range(8):
				if i + j < len(bits):
					byte = (byte << 1) | bits[i + j]
			bytes_list.append(byte)
		
		return bytes(bytes_list)
	
	def hash_password(self, password: str, hash_algorithm: str) -> str:
		password_bytes = password.encode('utf-8')

		if hash_algorithm == 'ready':
			hash_result = self.hash_func.ready_hash(password_bytes, 'sha256')
			return hash_result.hex()
		if hash_algorithm == 'ma_prime':
			hash_int = self.hash_func.ma_prime_hash(password_bytes)
			return hex(hash_int)[2:].zfill(8)
		if hash_algorithm == 'gost':
			hash_result = self.hash_func.gost_341194_hash(password_bytes)
			return hash_result.hex()
		
		raise ValueError(f"Неизвестный алгоритм хеширования: {hash_algorithm}")
