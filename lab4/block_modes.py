from block_utils import split_into_blocks, combine_blocks
from block_ciphers import Scrambler
import hashlib
import os


class CBCMode:
	def __init__(self, cipher, iv, bytes = None) -> None:
		self.cipher = cipher
		self.block_size = cipher.block_size

		if iv is None:
			self.iv = os.urandom(self.block_size)
		else:
			if len(iv) != self.block_size:
				raise ValueError(f"IV должен быть длиной {self.block_size} байт")
			self.iv = iv
	
	def _xor_blocks(self, block1: bytes, block2: bytes) -> bytes:
		return bytes(a ^ b for a, b in zip(block1, block2))
	
	def ecnrypt(self, data: bytes) -> bytes:
		blocks = split_into_blocks(data, self.block_size)
		encrypted_blocks = []
		previous_block = self.iv

		for block in blocks:
			xored_block = self._xor_blocks(block, previous_block)
			encrypted_block = self.cipher._encrypt_block(xored_block)
			encrypted_blocks.append(encrypted_block)
			previous_block = encrypted_block
		
		return self.iv + combine_blocks(encrypted_blocks)
	
	def decrypt(self, data: bytes) -> bytes:
		iv = data[:self.block_size]
		encrypted_data = data[self.block_size:]
		blocks = split_into_blocks(encrypted_data, self.block_size)
		decrypted_blocks = []
		previous_block = iv

		for block in blocks:
			decrypted_block = self.cipher._decrypt_block(block)
			plain_block = self._xor_blocks(decrypted_block, previous_block)
			decrypted_blocks.append(plain_block)
			previous_block = block
		
		return combine_blocks(decrypted_blocks)


class CBCScrambler:
	def __init__(self, password: str, block_size: int = 7, hash_algoritm: str = 'gost',
		     generator_type: str = 'yarrow160', iv: bytes = None) -> None:
		self.scrambler = Scrambler(password, block_size, hash_algoritm, generator_type)
		self.cbc_mode = CBCMode(self.scrambler, iv)
		self.block_size = block_size

	def encrypt(self, data: bytes) -> bytes:
		return self.cbc_mode.ecnrypt(data)

	def decrypt(self, data: bytes) -> bytes:
		return self.cbc_mode.decrypt(data)

	@property
	def iv(self) -> bytes:
		return self.cbc_mode.iv

