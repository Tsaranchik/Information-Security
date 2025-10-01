class Generator:
	def __init__(self, seq_len: int = 10000, seed: int = 42) -> None:
		self.seq_len = seq_len
		self.seed = seed
		self.a = 1664525
		self.b = 1
		self.c = 1013904223
		self.m = 2 ** 32 - 1
	
	def quadratic_congruential_generator(self) -> list[int]:
		bit_seq = []
		x_prev = self.seed

		for _ in range(self.seq_len):
			x_next = (self.a * x_prev ** 2 + self.b * x_prev + self.c) % self.m
			bit = x_next & 1
			bit_seq.append(bit)
			x_prev = x_next
		
		return bit_seq