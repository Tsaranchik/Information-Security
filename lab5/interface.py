# interface.py
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich import print
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
import json
import os
import time
from prime_generator import PrimeGenerator
from elgamal import ElGamal

class Interface:
	def __init__(self) -> None:
		self.console = Console()
		self.config_path = "config_lab5.json"
		self.config = self._load_config()
		self.prime_gen = PrimeGenerator()
		self.elgamal = ElGamal()
		self.current_public_key = None
		self.current_private_key = None
	
	def _load_config(self) -> dict:
		try:
			with open(self.config_path, "r", encoding='utf-8') as f:
				return json.load(f)
		except FileNotFoundError:
			default_config = {
				"input_file_path": "",
				"output_file_path": "",
				"key_file_path": "",
				"prime_bits": 128
			}
			with open(self.config_path, "w", encoding='utf-8') as f:
				json.dump(default_config, f, indent=4)
			
			return default_config
	
	def _save_config(self):
		with open(self.config_path, "w", encoding='utf-8') as f:
			json.dump(self.config, f, indent=4)
	
	def print_title(self) -> None:
		self.console.clear()
		self.console.rule(
			'Лабораторная работа №5\nАсимметричная криптография - алгоритм Эль-Гамаля', 
			style="blue"
		)
	
	def print_menu(self) -> None:
		print(Panel.fit(
			"[bold cyan] Главное меню [/bold cyan]",
			style="cyan",
		))

		print("1. Генерация простых чисел")
		print("2. Создание пары ключей")
		print("3. Шифрование файла")
		print("4. Дешифрование файла")
		print("5. Просмотр ключей")
		print("6. Сохранение ключей в файл")
		print("7. Загрузка ключей из файла")
		print("8. Настройки")
		print("9. Выход")

		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"],
			default="1"
		)

		if choice == "1":
			self.generate_primes_menu()
		elif choice == "2":
			self.generate_keys_menu()
		elif choice == "3":
			self.encrypt_menu()
		elif choice == "4":
			self.decrypt_menu()
		elif choice == "5":
			self.view_keys_menu()
		elif choice == "6":
			self.save_keys_menu()
		elif choice == "7":
			self.load_keys_menu()
		elif choice == "8":
			self.settings_menu()
		elif choice == "9":
			print("Завершение программы...")
			time.sleep(0.5)
			self.console.clear()
			exit(0)
	
	def _get_file_path(self, prompt_text: str, 
			   default_path: str = "", is_save: bool = False) -> str | None:
		if default_path and os.path.exists(default_path):
			suggested_path = default_path
		else:
			suggested_path = ""
		
		path = Prompt.ask(
			f"[bold yellow]{prompt_text}[/bold yellow]",
			default=suggested_path
		)

		if not is_save and path and not os.path.exists(path):
			print("[red]Файл не существует.[/red]")
			if not Prompt.ask("[bold yellow]Всё равно продолжить? (y/n)[/bold yellow]", 
							choices=["y", "n"], default="n") == "y":
				return None

		return path
	
	def generate_primes_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold green] Генерация простых чисел [/bold green]",
			style="green"
		))

		bits = int(Prompt.ask(
			"[bold yellow]Введите длину простых чисел в битах[/bold yellow]",
			default=str(self.config.get("prime_bits", 128))
		))

		count = int(Prompt.ask(
			"[bold yellow]Сколько простых чисел сгенерировать?[/bold yellow]",
			default="5"
		))

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Генерация простых чисел...", total=count)
			
			primes = []
			for i in range(count):
				prime = self.prime_gen.generate_large_prime(bits)
				primes.append(prime)
				progress.update(task, completed=i+1)
		
		# Выводим результаты
		table = Table(show_header=True, header_style="bold magenta")
		table.add_column("№", style="dim", width=6)
		table.add_column("Простое число (десятичное)")
		table.add_column("Длина (бит)")

		for i, prime in enumerate(primes, 1):
			table.add_row(
				str(i),
				str(prime),
				str(prime.bit_length())
			)

		print("\n[green]Сгенерированные простые числа:[/green]")
		print(table)

		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def generate_keys_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold green] Генерация пары ключей [/bold green]",
			style="green"
		))

		bits = int(Prompt.ask(
			"[bold yellow]Введите длину ключей в битах[/bold yellow]",
			default=str(self.config.get("prime_bits", 128))
		))

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Генерация ключей...", total=100)
			
			self.current_public_key, self.current_private_key = self.elgamal.generate_keys(bits)
			progress.update(task, completed=100)
		
		print("\n[green]Ключи успешно сгенерированы![/green]")
		
		self._display_key_info()
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def _display_key_info(self):
		"""Отображение информации о текущих ключах"""
		if self.current_public_key and self.current_private_key:
			table = Table(show_header=True, header_style="bold cyan")
			table.add_column("Параметр", style="dim")
			table.add_column("Значение")
			
			table.add_row("p (простое число)", str(self.current_public_key['p']))
			table.add_row("Длина p (бит)", str(self.current_public_key['p'].bit_length()))
			table.add_row("g (генератор)", str(self.current_public_key['g']))
			table.add_row("y (открытый ключ)", str(self.current_public_key['y']))
			table.add_row("x (закрытый ключ)", str(self.current_private_key['x']))
			
			print(table)
		else:
			print("[red]Ключи не сгенерированы[/red]")
	
	def encrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Шифрование файла [/bold blue]",
			style="blue"
		))

		if not self.current_public_key:
			print("[red]Сначала сгенерируйте ключи![/red]")
			Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
			return

		input_file = self._get_file_path(
			"Введите путь к файлу для шифрования",
			self.config.get("input_file_path", "")
		)
		
		if input_file is None:
			return

		output_file = self._get_file_path(
			"Введите путь для сохранения зашифрованного файла",
			self.config.get("output_file_path", ""),
			is_save=True
		)

		self.config["input_file_path"] = input_file
		self.config["output_file_path"] = output_file
		self._save_config()

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Шифрование...", total=100)
			
			success = self.elgamal.encrypt_file(input_file, output_file, self.current_public_key)
			progress.update(task, completed=100)
		
		if success:
			input_size = os.path.getsize(input_file)
			output_size = os.path.getsize(output_file)
			
			print("\n[green]Файл успешно зашифрован![/green]")
			print(f"[cyan]Размер исходного файла:[/cyan] {input_size} байт")
			print(f"[cyan]Размер зашифрованного файла:[/cyan] {output_size} байт")
			print(f"[cyan]Коэффициент увеличения:[/cyan] {output_size/input_size:.2f}x")
		else:
			print("[red]Ошибка при шифровании файла![/red]")
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def decrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold green] Дешифрование файла [/bold green]",
			style="green"
		))

		if not self.current_private_key:
			print("[red]Сначала сгенерируйте или загрузите ключи![/red]")
			Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
			return

		input_file = self._get_file_path(
			"Введите путь к зашифрованному файлу",
			self.config.get("output_file_path", "")
		)
		
		if input_file is None:
			return

		output_file = self._get_file_path(
			"Введите путь для сохранения дешифрованного файла",
			self.config.get("output_file_path", ""),
			is_save=True
		)

		self.config["output_file_path"] = input_file
		self._save_config()

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Дешифрование...", total=100)
			
			success = self.elgamal.decrypt_file(input_file, output_file, self.current_private_key)
			progress.update(task, completed=100)
		
		if success:
			print("\n[green]Файл успешно дешифрован![/green]")
			
			try:
				with open(output_file, 'r', encoding='utf-8') as f:
					content = f.read(500) 
					print(f"\n[cyan]Содержимое (первые 500 символов):[/cyan]")
					print(content + ("..." if len(content) == 500 else ""))
			except:
				print("[dim]Невозможно отобразить содержимое (бинарный файл)[/dim]")
		else:
			print("[red]Ошибка при дешифровании файла![/red]")
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def view_keys_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold magenta] Просмотр ключей [/bold magenta]",
			style="magenta"
		))

		self._display_key_info()
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def save_keys_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold cyan] Сохранение ключей в файл [/bold cyan]",
			style="cyan"
		))

		if not self.current_public_key or not self.current_private_key:
			print("[red]Нет ключей для сохранения![/red]")
			Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
			return

		key_file = self._get_file_path(
			"Введите путь для сохранения ключей",
			self.config.get("key_file_path", ""),
			is_save=True
		)

		try:
			with open(key_file, 'w') as f:
				f.write("PUBLIC_KEY:\n")
				f.write(f"p={self.current_public_key['p']}\n")
				f.write(f"g={self.current_public_key['g']}\n")
				f.write(f"y={self.current_public_key['y']}\n")
				
				f.write("PRIVATE_KEY:\n")
				f.write(f"p={self.current_private_key['p']}\n")
				f.write(f"x={self.current_private_key['x']}\n")
			
			self.config["key_file_path"] = key_file
			self._save_config()
			
			print("[green]Ключи успешно сохранены![/green]")
		except Exception as e:
			print(f"[red]Ошибка при сохранении ключей: {e}[/red]")
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def load_keys_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Загрузка ключей из файла [/bold blue]",
			style="blue"
		))

		key_file = self._get_file_path(
			"Введите путь к файлу с ключами",
			self.config.get("key_file_path", "")
		)
		
		if key_file is None:
			return

		try:
			with open(key_file, 'r') as f:
				lines = f.readlines()
			
			public_key = {}
			private_key = {}
			current_section = None
			
			for line in lines:
				line = line.strip()
				if line == "PUBLIC_KEY:":
					current_section = "public"
				elif line == "PRIVATE_KEY:":
					current_section = "private"
				elif '=' in line:
					key, value = line.split('=')
					if current_section == "public":
						public_key[key] = int(value)
					elif current_section == "private":
						private_key[key] = int(value)
			
			if public_key and private_key:
				self.current_public_key = public_key
				self.current_private_key = private_key
				print("[green]Ключи успешно загружены![/green]")
				self._display_key_info()
			else:
				print("[red]Не удалось загрузить ключи из файла[/red]")
				
		except Exception as e:
			print(f"[red]Ошибка при загрузке ключей: {e}[/red]")
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def settings_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold magenta] Настройки [/bold magenta]"
		))

		print("1. Настройки путей к файлам")
		print("2. Настройки генерации ключей")
		print("3. Назад")

		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices=["1", "2", "3"],
			default="1"
		)

		if choice == "1":
			self._file_path_settings()
		elif choice == "2":
			self._key_generation_settings()
	
	def _file_path_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print("Текущие настройки путей:")
		print(f"Входной файл: {self.config.get('input_file_path', 'не указан')}")
		print(f"Выходной файл: {self.config.get('output_file_path', 'не указан')}")
		print(f"Файл ключей: {self.config.get('key_file_path', 'не указан')}")
		self.console.rule(style="blue")

		print("1. Изменить путь до входного файла")
		print("2. Изменить путь до выходного файла")
		print("3. Изменить путь до файла ключей")
		print("4. Очистить все пути")
		print("5. Назад")

		setting = Prompt.ask(
			"[bold yellow]Выберите настройку[/bold yellow]",
			choices=["1", "2", "3", "4", "5"],
			default="1"
		)

		if setting == "1":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для входного файла[/bold yellow]")
			self.config["input_file_path"] = new_path
		elif setting == "2":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для выходного файла[/bold yellow]")
			self.config["output_file_path"] = new_path
		elif setting == "3":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для файла ключей[/bold yellow]")
			self.config["key_file_path"] = new_path
		elif setting == "4":
			self.config["input_file_path"] = ""
			self.config["output_file_path"] = ""
			self.config["key_file_path"] = ""
			print("[green]Все пути очищены[/green]")
		elif setting == "5":
			return

		self._save_config()
		print("[green]Настройки сохранены![/green]")
		Prompt.ask("[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")
	
	def _key_generation_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print("Текущие настройки генерации ключей:")
		print(f"Длина простых чисел: {self.config.get('prime_bits', 128)} бит")
		self.console.rule(style="blue")

		new_bits = Prompt.ask(
			"[bold yellow]Введите новую длину простых чисел в битах[/bold yellow]",
			default=str(self.config.get("prime_bits", 128))
		)

		try:
			self.config["prime_bits"] = int(new_bits)
			self._save_config()
			print("[green]Настройки сохранены![/green]")
		except ValueError:
			print("[red]Некорректное значение![/red]")
		
		Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def main_loop(self) -> None:
		while True:
			self.print_title()
			self.print_menu()
