from typing import Optional, Callable
from generator import Generator
import random
import math
import json

CONST = 1.82138636 # Критическое значение статистики для всех тестов


def generate_bit_seq(
		generator_fn: Callable,
		seq_len: Optional[int] = 10000,
		input_file_path: Optional[str] = "",
		output_file_path: Optional[str] = "",
		seed: int = 42
) -> list[int]:
	"""
	Генерирует или загружает последовательность битов (0 и 1).

	Args:
		seq_len: Длина генерируемой последовательности (по умолчанию 10000 бит)
		input_file_path: Путь к файлу для загрузки последовательности
		output_file_path: Путь для сохранения последовательности
		seed: Seed для генератора случайных чисел

	Returns:
		list[int]: последовательность битов (0 и 1).
	
	Note:
		Если указан input_file_path, последовательность загружается из файла.
		Иначе генерируется случайная последовательность заданной длины.
	"""
	bit_seq = None
	generator = Generator(seq_len, seed)

	if input_file_path != "":
		with open(input_file_path, "r", encoding="utf-8") as f:
			bit_seq = list(f.read())
			bit_seq = [int(bit) for bit in bit_seq]

	bit_seq = generator.generator_fn if bit_seq is None else bit_seq

	if output_file_path != "":
		with open(output_file_path, "w", encoding="utf-8") as f:
			f.write("".join(map(str, bit_seq)))
		
	return bit_seq


def frequency_test(bit_seq: list[int]) -> bool:
	"""
	Частотный тест (Frequency Test).

	Проверяет пропорцию нулей и единиц в последовательности.
	Определяет, является ли кол-во нулей и единиц приблизительно таким же,
	как в истинно случайно последовательности.

	Args:
		bit_seq: Последовательность битов (0 и 1)

	Returns:
		bool: True если тест пройден (последовательность случайна), False в противном
		случае

	Algorithm:
		1. Преобразование битов в значения -1 и 1
		2. Вычисление суммы S_n
		3. Вычисление статистики S = |S_n| / sqrt(n)
		4. Сравнение с критическим значением CONST
	"""
	fixed_bit_seq = [2 * bit - 1 for bit in bit_seq]
	S_n = sum(fixed_bit_seq)
	if (abs(S_n) / (math.sqrt(len(bit_seq)))) <= CONST:
		return True
	return False


def r(bit_seq: list[int], k: int):
	"""
	Вспомогательная функция для теста на последовательность одинаковых бит.

	Определяет, является ли k-тый бит началом новой цепочки.

	Args:
		bit_seq: Последовательность битов
		k: Индекс текущего бита
	
	Returns:
		int: 1 если бит k и k+1 разные (начало новой цепочки) 0 если одинаковые
	"""
	if bit_seq[k] == bit_seq[k + 1]:
		return 0
	return 1


def identical_bit_seq_test(bit_seq: list[int]) -> bool:
	"""
	Тест на последовательность одинаковых бит (Rusn Test).

	Анализирует количество цепочек (непрерывных последовательностей одинаковых бит)
	в проверяемой последовательности

	Args:
		bit_seq: Последовательность битов (0 и 1)
	
	Returns:
		bool: True если тест пройден, False в противном случае
	
	Algorithm:
		1. Вычисление частоты единиц (pi)
		2. Вычисление количества переходов V_n
		3. Вычисление статистики S
		4. Сравнение с критическим значением CONST
	"""
	pi = 1 / (len(bit_seq)) * sum(bit_seq)
	V_n = sum([r(bit_seq, k) for k in range(len(bit_seq) - 1)]) + 1
	S = abs(V_n - 2 * len(bit_seq) * pi * (1 - pi))
	S /= 2 * math.sqrt(2 * len(bit_seq) * pi * (1 - pi))
	if S <= CONST:
		return True
	return False


def extended_random_deviation_test(bit_seq: list[int]) -> bool:
	"""
	Расширенный тест на произвольные отклонения.

	Оценивает общее число посещений определенного состояния при произвольном обходе
	кумулятивный суммы. Состоит из 18 подтестов для состояний из -9 до 9 (кроме 0).

	Args:
		bit_seq: Последовательность битов (0 и 1)
	
	Returns:
		bool: True если все 18 тестов пройдены, False если хотя бы один не пройден
	
	Algorithm:
		1. Преобразование битов в -1 и 1
		2. Вычисление кумулятивных сумм
		3. Фомирование расширенной последовательности S'
		4. Подсчёт количества нулей L
		5. Вычисление количества посещений каждого состояния
		6. Вычисление статистик Y_j для каждого состояния
		7. Проверка всех статистик на превышение CONST
	"""
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
	

def run_tests(seq_len: int, config_path: str, generator_fn: Callable) -> tuple[list[int], dict]:
	"""
	Основная функция для запуска всех тестов псевдослучайных последовательностей.

	Args: 
		seq_len: Длина последовательности для генерации
	
	Returns:
		tuple: (строковое представление последовательности, словарь с результатами тестов)
	
	Note:
		Загружает конфигурацию из config.json, генерирует/загружает последовательность
		выполняет все три теста и возвращает результаты
	"""
	with open(config_path, "r", encoding="utf-8") as f:
		config = json.load(f)
	
	bit_seq = generate_bit_seq(
		generator_fn,
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
