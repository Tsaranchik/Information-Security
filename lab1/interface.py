from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print
import json
import os
import time
from bits_tests import run_tests


class Interface:
	def __init__(self) -> None:
		self.console = Console()
		self.config_path = "/home/v_vedin/university/labs/FouthCourse/FirstTerm/Information-Security/lab1/config.json"
		with open(self.config_path, "r", encoding="utf-8") as f:
				self.config = json.load(f)
	
	def print_title(self) -> None:
		self.console.clear()
		self.console.rule('Федеральное государственное бюджетное образовательное ' \
				  'учреждение высшего образования "Ульяновский ' \
				  'государственный технический университет"', style="blue")
		self.console.print(
			"\nЛабораторная Работа №1\n" \
			"Дисциплина: Информационная Безопасность\n" \
			"Работа выполнена студентом группы ИВТАСбд-41 Ведином Владимиром Александровичом\n",
			justify="center"
		)
		self.console.rule(style="blue")
	
	def print_menu(self) -> None:
		print(Panel.fit(
			"[bold cyan] Главное Меню [/bold cyan]",
			style="cyan",
		))

		print("1. Старт программы")
		print("2. Инструкция")
		print("3. Настройки")
		print("4. Выход")

		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices = ["1", "2", "3", "4"],
			default="1"
		)

		if choice == "1":
			self.run_menu()
		elif choice == "2":
			self.help_menu()
		elif choice == "3":
			self.settings_menu()
		elif choice == "4":
			print("Завершение программыы...")
			time.sleep(0.5)
			self.console.clear()
			exit(0)
	
	def run_menu(self) -> None:
		seq_len = 10000
		if self.config["input_file_path"] == "":
			self.console.clear()
			self.console.rule(style="blue")

			print(Panel.fit(
				"[bold green] Запуск программы [/bold green]",
				style="green"
			))

			self.console.rule(style="blue")

			seq_len = int(Prompt.ask(
				"[bold yellow]Укажите длину генерируемой последовательности[/bold yellow]",
				default="10000"
			))
		self.console.clear()

		self.console.rule("Результаты тестов", style="blue")

		bit_seq, test_data = run_tests(seq_len)
		print("Вывод битов...")
		if self.config["input_file_path"] != "":
			print(
				"Последовательность прочитанная из файла:\n"
				f"{bit_seq}"
			)
		else:
			print(
				"Сгенерированная последовательность\n"
				f"{bit_seq}"
			)
		
		
		for name, res in test_data.items():
			print(f"Результаты {name}: ", end="")
			if res == True:
				text = "пройден"
				style = "green"
			else:
				text = "непройден"
				style = "red"

			self.console.print(text, style=style)

			if res == False:
				print("Последовательность не случайна")
				Prompt.ask(
					"[bold yellow]Нажмите любую кнопку, чтобы вернуться в главное меню[/bold yellow]"
				)
				break
		print("Все тесты пройдены, последовательность случайна")
		Prompt.ask(
				"[bold yellow]Нажмите любую кнопку, чтобы вернуться в главное меню[/bold yellow]"
		)
				
	
	def help_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Инструкция [/bold blue]"
		))
		print(
			"Это программа по тестированию последовательности бит на равномерность и случайность \n" \
			"В ней представлены такие тесты как:\n" \
			"\t1. Частотный тест (Оценка пропорции нулей и единиц в последовательности)\n" \
			"\t2. Тест на последовательность одинаковых бит (Анализ кол-ва непрерывных последовательностей одинаковых бит)\n" \
			"\t3. Расширенный тест на произвольные отклонения (Оцнека общего числа посещения состояния при произвольном обходе кумулятивной суммы)\n" \
			"\t\tСостояния - последовательность чисел вида [-9, -8, ..., -1, 1, 2, ..., 9]\n\n"
		)
		print(
			"Саму последовательность любой длинны (на выбор пользователя) можно как случайно генерировать" \
			" так и считывать из файла, путь до кторого пользователь может указать\n" \
			"Также, саму последовательность можно и сохранить в файл, снова указав до него путь\n" \
			"Указать путь до входного и выходного файла можно в настройках\n\n"
		)
		print(
			"Тесты проводятся по очереди (от 1 до 3, как указано выше). Если какой-то из тестов не проходит, то остальные не проводятся\n"
		)

		self.console.rule(style="blue")

		Prompt.ask(
			"[bold yellow]Нажмите любую кнопку чтобы выйти[/bold yellow]",
		)

		return

	def settings_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold magenta] Настройки [/bold magenta]"
		))

		print(
			"1. Указать путь до входного файла\n" \
			"2. Указать путь до выходного файла\n" \
			"3. Выход\n" \
		)
		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices = ["1", "2", "3"],
			default="1"
		)

		if choice == "1" or choice == "2":
			choices_str_dict = {
				"1": "входного",
				"2": "выходного"
			}
			choices_keys_dict = {
				"1": "input_file_path",
				"2": "output_file_path"
			}

			

			self.console.clear()
			self.console.rule(style="blue")
			print(
				f"Текущий путь до {choices_str_dict[choice]} файла: " \
				f"{self.config[choices_keys_dict[choice]] if self.config[choices_keys_dict[choice]] != "" else "не указан"}"
			)
			self.console.rule(style="blue")
			
			while True:
				file_path = Prompt.ask(
					f"[bold yellow]Введите путь до {choices_str_dict[choice]} файла или введите 0 для сброса[/bold yellow]",
					default="Нажмите enter, чтобы вернуться назад"
				)

				if file_path == "0":
					self.config[choices_keys_dict[choice]] = ""
					with open(self.config_path, "w", encoding="utf-8") as f:
						json.dump(self.config, f, indent=4)
					print("Путь до файла сброшен")
					break
				
				if file_path == "Нажмите enter, чтобы вернуться назад":
					break

				if os.path.exists(file_path) and os.path.isfile(file_path):
					self.config[choices_keys_dict[choice]] = file_path
					with open(self.config_path, "w", encoding="utf-8") as f:
						json.dump(self.config, f, indent=4)
					print("Путь до файла успешно сохранён")
					break

				print("Такого файла не существует или путь указан неверно попробуйте ещё раз")
	
	def main_loop(self) -> None:
		while True:
			self.console.clear()
			self.print_title()
			self.print_menu()
