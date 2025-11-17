from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import json
import os
import time
from stream_cipher import StreamCipher

class Interface:
	def __init__(self) -> None:
		self.console = Console()
		self.config_path = "config.json"
		self.config = self._load_config()
		self.cipher = StreamCipher()
	
	def _load_config(self) -> dict:
		try:
			with open(self.config_path, "r", encoding='utf-8') as f:
				return json.load(f)
		except FileNotFoundError:
			default_config = {
				"input_file_path": "",
				"output_file_path": "",
				"default_hash_algorithm": "ready",
				"default_generator": "yarrow160"
			}
			with open(self.config_path, "w", encoding='utf-8') as f:
				json.dump(default_config, f, indent=4)
			
			return default_config
	
	def print_title(self) -> None:
		self.console.clear()
		self.console.rule(
			'Федеральное государственное бюджетное образовательное ' \
			'учреждение высшего образования "Ульяновский' \
			'государственный техникческий университет"', style="blue"
		)
		self.console.print(
			"\nЛабораторная Работа №3\n" \
			"Потоковые шифры, функции хеширования\n" \
			"Дисциплина: Информационная Безопасность\n" \
			"Работа выполнена студентов группы ИВТАСбд-41 Ведином Владимиром Алесандровичем\n",
			justify="center"
		)
		self.console.rule(style="blue")
	
	def print_menu(self) -> None:
		print(Panel.fit(
			"[bold cyan] Главное меню [/bold cyan]",
			style="cyan",
		))

		print("1. Шифрование файла")
		print("2. Дешифрование файла")
		print("3. Хеширования пароля")
		print("4. Инструкция")
		print("5. Настройки")
		print("6. Выход")

		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices=["1", "2", "3", "4", "5", "6"],
			default="1"
		)

		if choice == "1":
			self.encrypt_menu()
		elif choice == "2":
			self.decrypt_menu()
		elif choice == "3":
			self.hash_menu()
		elif choice == "4":
			self.help_menu()
		elif choice == "5":
			self.settings_menu()
		elif choice == "6":
			print("Завершение программы...")
			time.sleep(0.5)
			self.console.clear()
			exit(0)
	
	def encrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold green] Шифрование файла [/bold green]",
			style="green"
		))

		input_file = Prompt.ask(
			"[bold yellow]Введите путь к файлу для шифрования[/bold yellow]",
			default=self.config.get("input_file_path", "")
		)
		
		if not os.path.exists(input_file):
			print("[red]Файл не существует![/red]")
			Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")

			return
		
		self.config["input_file_path"] = input_file

		output_file = Prompt.ask(
			"[bold yellow]Введите путь для сохранения зашифрованного файла[/bold yellow]",
			default=self.config.get("output_file_path", "")
		)

		self.config["output_file_path"] =output_file

		password = Prompt.ask(
			"[bold yellow]Введите пароль для шифрования[/bold yellow]",
			password=True
		)

		hash_algo = Prompt.ask(
			"[bold yellow]Выберите алгоритм хеширования[/bold yellow]",
			choices=["ready", "ma_prime", "gost"],
			default=self.config.get("default_hash_algorithm", "ready")
		)

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Шифрование...", total=100)
			success = self.cipher.encrypt_decrypt_file(
				input_file, output_file, password, hash_algo, "yarrow160"
			)

			progress.update(task, completed=100)
		
		if success:
			with open(input_file, 'r', encoding='utf-8') as f:
				print(f"\nСодержимое файла для шифровки:\n{f.read()}")
			print("[green]Файл успешно зашифрован![/green]\n")
			with open (output_file, 'rb') as f:
				print(f"Результаты шифровки:\n{f.read()}")
		else:
			print("[red]Ошибка при шифровании файла![/red]")
		
		with open(self.config_path, "w", encoding='utf-8') as f:
			json.dump(self.config, f, indent=4)
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def decrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Дешифрование файла [/bold blue]",
			style="blue"
		))

		input_file = Prompt.ask(
			"[bold yellow]Введите путь к зашифрованному файлу[/bold yellow]",
			default=self.config.get("output_file_path", "")
		)

		if not os.path.exists(input_file):
			print("[red]Файл не существует![/red]")
			Prompt.ask("[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")

			return

		output_file = Prompt.ask(
			"[bold yellow]Введите путь для сохранения дешифрованного файла[/bold yellow]",
			default=self.config.get("output_file_path", "")
		)

		password = Prompt.ask(
			"[bold yellow]Введите пароль для дешифрования[/bold yellow]",
			password=True
		)

		hash_algo = Prompt.ask(
			"[bold yellow]Выберите алгоритм хеширования[/bold yellow]",
			choices=["ready", "ma_prime", "gost"],
			default=self.config.get("default_hash_algirithm", "gost")
		)

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Дешифрование...", total=100)
			success = self.cipher.encrypt_decrypt_file(
				input_file, output_file, password, hash_algo, "yarrow160"
			)

			progress.update(task, completed=100)
		
		if success:
			print("\n[green]Файл успешно дешифрован![/green]")
			with open(output_file, "r", encoding='utf-8') as f:
				print(f"\nРезультат дешифровки:\n{f.read()}")
			
		else:
			print("[red]Ошибка при дешифровании файла![/red]")
		
		with open(self.config_path, "w", encoding='utf-8') as f:
			json.dump(self.config, f, indent=4)
		
		Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def hash_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")
		
		print(Panel.fit(
			"[bold magenta] Хеширование пароля [/bold magenta]",
			style="magenta"
		))

		password = Prompt.ask(
			"[bold yellow]Введите пароль для хеширования[/bold yellow]"
		)

		hash_algo = Prompt.ask(
			"[bold yellow]Выберите алгоритм хеширования[/bold yellow]",
			choices=["ready", "ma_prime", "gost"],
			default=self.config.get("default_hash_algorithm", "gost")
		)

		hash_value = self.cipher.hash_password(password, hash_algo)

		table = Table(show_header=True, header_style='bold cyan')
		table.add_column("Алгоритм", style="dim", width=12)
		table.add_column("Хеш-значение")

		table.add_row(
			hash_algo.upper(),
			hash_value
		)

		print(table)

		Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def help_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Инструкция [/bold blue]"
		))

		print(
			"Эта программа предназначена для потокового шифрования файлов и хеширования паролей.\n\n"
			"[bold]Основные возможности:[/bold]\n"
			"• Шифрование и дешифрование файлов любого размера\n"
			"• Хеширование паролей с использованием различных алгоритмов\n"
			"• Использование различных генераторов псевдослучайных чисел\n\n"
			"[bold]Алгоритмы хеширования:[/bold]\n"
			"• [cyan]ready[/cyan] - готовая функция (SHA-256)\n"
			"• [cyan]ma_prime[/cyan] - собственная реализация MaPrime\n"
			"• [cyan]gost[/cyan] - собственная реализация ГОСТ Р 34.11-94\n\n"
			"[bold]Генераторы ПСЧ:[/bold]\n"
			"• [cyan]yarrow160[/cyan] - криптографический генератор Yarrow-160\n\n"
			"[bold]Принцип работы:[/bold]\n"
			"1. Пароль хешируется выбранным алгоритмом\n"
			"2. Хеш используется для инициализации генератора ПСЧ\n"
			"3. Генератор создает ключевой поток\n"
			"4. Ключевой поток накладывается на данные операцией XOR\n"
			"5. Для дешифрования используется тот же пароль и алгоритм\n"
		)

		self.console.rule(style="blue")
		Prompt.ask("[bold yellow]Нажмите любую кнопку, чтобы выйти[/bold yellow]")
	
	def settings_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold magenta] Настройки [/bold magenta]"
		))

		print(
			"1. Настройки путей к файлам\n" \
			"2. Настройки по умолчанию\n" \
			"3. Выход\n" \
		)
		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices=["1", "2", "3"],
			default="1"
		)

		if choice == "1":
			self._file_path_settings()
		elif choice == "2":
			self._default_settings()
	
	def _file_path_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print("Текущие настройки путей:")
		print(f"Входной файл: {self.config.get("input_file_path", "не указан")}")
		print(f"Выходной файл: {self.config.get('output_file_path', "не указан")}")
		self.console.rule(style="blue")

		setting = Prompt.ask(
			"[bold yellow]Выберите настройку[/bold yellow]",
			choices=["1", "2", "3"],
			default="1"
		)

		if setting == "1":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для входного файла[/bold yellow]")
			self.config["input_file_path"] = new_path
		elif setting == "2":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для выходного файла[/bold yellow]")
			self.config["output_file_path"] = new_path

		with open(self.config_path, "w", encoding='utf-8') as f:
			json.dump(self.config, f, indent=4)
		
		print("[green]Настройки сохранены![/green]")
		Prompt.ask("[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")
	
	def _default_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print("Текущие настройки по умолчанию:")
		print(f"Алгоритм хеширования: {self.config.get('default_hash_algirithm', 'ready')}")
		print(f"Генератор ПСЧ: {self.config.get('default_generator', 'yarrow160')}")
		self.console.rule(style="blue")

		setting = Prompt.ask(
			"[bold yellow]Выберите настройку[/bold yellow]",
			choices=["1", "2", "3"],
			default="1"
		)

		if setting == "1":
			new_algo = Prompt.ask(
				"[bold yellow]Выберите алгоритм хеширования по умолчанию[/bold yellow]",
				choices=["ready", "ma_prime", "gost"],
				default=self.config.get("default_hash_algorithm", "ready")	
			)
			self.config["default_hash_algorithm"] = new_algo
		elif setting == "2":
			new_gen = Prompt.ask(
				"[bold yellow]Выберите генератор ПСЧ по умолчанию[/bold yellow]",
				choices=["quadratic", "bbs", "yarrow160"],
				default=self.config.get("default_generator", "yarrow160")
			)
			self.config["default_generator"] = new_gen

		with open(self.config_path, "w", encoding='utf-8') as f:
			json.dump(self.config, f, indent=4)
		
		print("[green]Настройки сохранены![/green]")
		Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def main_loop(self) -> None:
		while True:
			self.print_title()
			self.print_menu()
	