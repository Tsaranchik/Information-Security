from typing import Optional
import random
import os
import math
import json

CONST = 1.82138636


def generate_bit_seq(
		seq_len: Optional[int] = 10000,
		input_file_path: Optional[str] = "",
		output_file_path: Optional[str] = "",
		seed: int = 42
) -> list[int]:
	bit_seq = None
	random.seed(seed)

	if input_file_path != "":
		with open(input_file_path, "r", encoding="utf-8") as f:
			bit_seq = list(f.read())
			bit_seq = [int(bit) for bit in bit_seq]

	bit_seq = [0 if random.random() < 0.5 else 1 for _ in range(seq_len)] if bit_seq is None else bit_seq

	if output_file_path != "":
		with open(output_file_path, "w", encoding="utf-8") as f:
			f.write("".join(map(str, bit_seq)))
		
	return bit_seq


def frequency_test(bit_seq: list[int]) -> bool:
	fixed_bit_seq = [2 * bit - 1 for bit in bit_seq]
	S_n = sum(fixed_bit_seq)
	if (abs(S_n) / (math.sqrt(len(bit_seq)))) <= CONST:
		return True
	return False


def r(bit_seq: list[int], k: int):
	if bit_seq[k] == bit_seq[k + 1]:
		return 0
	return 1


def identical_bit_seq_test(bit_seq: list[int]) -> bool:
	pi = 1 / (len(bit_seq)) * sum(bit_seq)
	V_n = sum([r(bit_seq, k) for k in range(len(bit_seq) - 1)]) + 1
	S = abs(V_n - 2 * len(bit_seq) * pi * (1 - pi))
	S /= 2 * math.sqrt(2 * len(bit_seq) * pi * (1 - pi))
	if S <= CONST:
		return True
	return False


def extended_random_deviation_test(bit_seq: list[int]) -> bool:
	states = [str(i) for i in range(-9, 10) if i != 0]
	fixed_bit_seq = [2 * bit - 1 for bit in bit_seq]
	S = [0, fixed_bit_seq[0]]

	fixed_bit_seq = fixed_bit_seq[1:]

	S.extend([S.append(S[-1] + bit) for bit in fixed_bit_seq])

	S.append(0)

	L = S.count(0)
	theta = {state: S.count(int(state)) for state in states}

	Y = {
		j: (abs(theta[j]) - L) / math.sqrt(2 * L * (4 * abs(int(j)) - 2)) 
		for j in states
	}

	if all([y < CONST for y in list(Y.values())]):
		return True
	return False
	

def run_tests(seq_len: Optional[int]) -> tuple[list[int], dict]:
	config_path = "/home/v_vedin/university/labs/FouthCourse/FirstTerm/Information-Security/lab1/config.json"
	with open(config_path, "r", encoding="utf-8") as f:
		config = json.load(f)
	
	bit_seq = generate_bit_seq(
		seq_len, config["input_file_path"],
		config["output_file_path"]
	)
	
	str_bit_seq = "".join(str(bit) for bit in bit_seq)

	test_results = {
		"Частотный тест": frequency_test(bit_seq),
		"Тест на последовательность одинаковых бит": identical_bit_seq_test(bit_seq),
		"Расширенный тест на произвольные отклонения": extended_random_deviation_test(bit_seq)
	}

	return str_bit_seq, test_results
