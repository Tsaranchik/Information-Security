import random
import hashlib
import time
import os
import sympy
import math
from Crypto.Cipher import DES


class Generator:
	"""
	Класс, объединяющий различные генераторы псевдослучайных битовых последовательностей:
	- Квадратичный конгруэнтный генератор (Quadratic Congruential Generator),
	- Генератор Блюма-Блюма-Шуба (BBS),
	- Генератор Yarrow-160.
	"""
	def __init__(self) -> None:
		"""
		Инициализирует экземпляр генератора без параметров
		"""
		...
	
	def quadratic_congruential_generator(self, seq_len: int = 10000) -> list[int]:
		"""
		Квадратичный конгруэнтный генератор псевдослучайной битовой последовательности.
		
		Использует рекуррентное соотношение:
		x_{n+1} = {a * x_n^2 + b * x_n + c} mod m

		Args:
			seq_len: длина генерируемой битовой последовательности (по умолчанию 10000)
		
		Returns:
			List[int]: список битов (0 и 1)
		"""
		a = 1664525
		b = 1
		c = 1013904223
		m = 2 ** 32 - 1
		seed = 42
		
		bit_seq = []
		x_prev = seed

		for _ in range(seq_len):
			x_next = (a * x_prev ** 2 + b * x_prev + c) % m
			bit = x_next & 1
			bit_seq.append(bit)
			x_prev = x_next
		
		return bit_seq
	
	def bbs_generator(self, seq_len: int = 10000) -> list[int]:
		"""
		Генератор Блюма-Блюма-Шуба (Blum-Blum-Shub).

		Алгоритм основан на трудности факторизации больших чисел:
			x_{n+1} = x_n^2 mod n, где n = p * q (p и q - большие простые числа)

		Args:
			seq_len: длина генерируемой битовой последовательности (по умолчанию 10000)
		
		Returns:
			List[int]: список битов (0 и 1)
		"""
		def generate_prime() -> int:
			"""
			Функция, генерирующая простое число длинной 160 бит.

			С помощью функции randprime из библиотеки sympy генерирует 
			простое число в диапазаоне от 2^159 до 2^160.

			Returns:
				int: большое простое число, удовлетворяющее условию: `prime ≡ 3 (mod 4)`
			"""
			bit_len = 160
			while True:
				prime = sympy.randprime(2**(bit_len - 1), 2**bit_len)
				if prime % 4 == 3:
					return prime
		p = 0
		q = 0
		while (p == q):
			p = generate_prime() 
			q = generate_prime()
			
		n = p * q
		
		while True:
			seed = random.randint(2, n-1)
			if math.gcd(seed, n) == 1:
				break

		x_prev = pow(seed, 2, n)
		bit_seq = []

		for _ in range(seq_len):
			x_next = pow(x_prev, 2, n)
			bit = x_next & 1
			bit_seq.append(bit)
			x_prev = x_next
		
		return bit_seq
	
	class Yarrow160:
		"""
		Реализация криптографического генератора Yarrow-160.

		Генератор основан на идее периодического обновления ключа K и счётчика C
		с использованием блочного шифра (DES) и хеш-функции (SHA-1)
		"""
		def __init__(
				self,
				n: int = 64,
				k: int = 64,
				Pg: int = 10,
				Pt: int = 20
		) -> None:
			"""
			Инициализирует параметры генератора Yarrow-160.

			Args:
				n: размер блока (бит)
				k: рзамер ключа (бит)
				Pg: порог обновления ключа K
				Pt: порог обновления ключа и счётчика
			"""
			self.n = n
			self.k = k
			self.Pg = Pg
			self.Pt = Pt
			self.curPg = Pg
			self.curPt = Pt
			self.C = 0
			self.K = os.urandom(8)
			self.t = 0
		
		def entropy_accumulator(self) -> bytes:
			"""
			Имитация наколепния энтропии.

			Генерирует псевдослучайные данные на основе системного времени, 
			PID процесса и случайных байт.

			Returns:
				bytes: SHA-1 хеш от собранных энтропийных данных
			"""
			data = f"{time.time_ns()}_{os.getpid()}_{os.urandom(8).hex()}".encode()
			return hashlib.sha1(data).digest()
		
		def update_key(self) -> None:
			"""
			Обновляет внутренний ключ K и счётчик C на сонове новой энтропии.
			"""
			entropy = self.entropy_accumulator()
			self.K = hashlib.sha1(self.K + entropy).digest()[:8]
			self.C = (self.C + 1) % (2 ** self.n)
		
		def encrypt_block(self, data: bytes) -> bytes:
			"""
			Шифрует блок данных с помощью DES в режиме ECB.

			Args:
				data: байты длиной 8 байт.
			
			Returns:
				bytes: зашифрованный блок длиной 8 байт
			"""
			cipher = DES.new(self.K, DES.MODE_ECB)
			return cipher.encrypt(data)
		
		def H(self, v: bytes, K: bytes) -> bytes:
			"""
			Хеш-функция H(v, K) = SHA-1(v || K)[:8].

			Args:
				v: байтовая последовательность
				k: ключ
			
			Returns:
				bytes: результат хеширования длиной 8 байт
			"""
			return hashlib.sha1(v + K).digest()[:8]
		
		def G(self, i: int) -> bytes:
			"""
			Функция G(i), генерирующая новые данные для ключа.

			Args:
				i: индекс итерации

			Returns:
				bytes: результат шифрования счётчика длиной 8 байт

			"""
			Ci = (self.C + i) % (2 ** self.n)
			Ci_bytes = Ci.to_bytes(8, "big")
			return self.encrypt_block(Ci_bytes)
		
		def generate_bits(self, seq_len: int = 10000):
			"""
			Генерирует псевдослучайную битовую последовательность.

			Args:
				seq_len: требуемая длина последовательности (по умолчанию 10000)
			
			Returns:
				List[int]: список битов (0 и 1)
			"""
			bit_seq = []

			while len(bit_seq) < seq_len:
				if self.curPg == 0:
					self.K = self.G(self.C)
					self.curPg = self.Pg
				
				if self.curPt == 0:
					v0 = hashlib.sha1(self.entropy_accumulator() + self.K).digest()[:8]
					v = v0
					for _ in range(2):
						v = hashlib.sha1(v + v0 + self.K).digest()[:8]
					self.K = self.H(v, self.K)
					self.update_key()
					self.curPt = self.Pt
				
				xi = self.encrypt_block(self.C.to_bytes(8, "big"))
				self.C = (self.C + 1) % (2 ** self.n)
				self.curPg -= 1
				self.curPt -= 1

				for byte in xi:
					for bit in range(8):
						bit_seq.append((byte >> (7 - bit)) & 1)
						if len(bit_seq) >= seq_len:
							break
					if len(bit_seq) >= seq_len:
						break
			
			return bit_seq
	
	def yarrow160_generator(self,  seq_len: int = 10000) -> list[int]:
		"""
		Интерфейсная функция для генерации последовательности Yarrow-160.

		Создаёт экземпляр внутреннего класса Yarrow160 и вызывает метод generate_bits.

		Args:
			seq_len: длина генерируемой последовательности (по умолчанию 10000)
		
		Returns:
			List[int]: список битов (0 и 1)
		"""
		gen = self.Yarrow160()
		bit_seq = gen.generate_bits(seq_len)
		return bit_seq
