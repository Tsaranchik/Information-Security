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
from block_ciphers import Scrambler, DESHandler, DESEEE3
from block_modes import CBCScrambler

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
				"default_hash_algorithm": "gost",
				"default_generator": "yarrow160",
				"block_cipher_settings": {
					"algorithm": "scrambler",
					"mode": "cbc",
					"block_size": 7,
				}
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
			'Федеральное государственное бюджетное образовательное ' \
			'учреждение высшего образования "Ульяновский' \
			'государственный техникческий университет"', style="blue"
		)
		self.console.print(
			"\nЛабораторная Работа №4\n" \
			"Блочные шифры, режим использования блочных шифров\n" \
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

		print("1. Потоковое шифрование файла")
		print("2. Потоковое дешифрование файла")
		print("3. Блочное шифрование файла")
		print("4. Блочное дешифрование файла")
		print("5. Хеширования пароля")
		print("6. Инструкция")
		print("7. Настройки")
		print("8. Выход")

		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices=["1", "2", "3", "4", "5", "6", "7", "8"],
			default="1"
		)

		if choice == "1":
			self.encrypt_menu()
		elif choice == "2":
			self.decrypt_menu()
		elif choice == "3":
			self.block_encrypt_menu()
		elif choice == "4":
			self.block_decrypt_menu()
		elif choice == "5":
			self.hash_menu()
		elif choice == "6":
			self.help_menu()
		elif choice == "7":
			self.settings_menu()
		elif choice == "8":
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
			if not Prompt.ask("[bold yellow]Всё равно продолжить? (y/n)[/bold yellow]", choices=["y", "n"], default="y") == "y":
				return None

		return path 
	
	def encrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold green] Потоковое шифрование файла [/bold green]",
			style="green"
		))

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

		password = Prompt.ask(
			"[bold yellow]Введите пароль для шифрования[/bold yellow]",
			password=True
		)

		hash_algo = Prompt.ask(
			"[bold yellow]Выберите алгоритм хеширования[/bold yellow]",
			choices=["ready", "ma_prime", "gost"],
			default=self.config.get("default_hash_algorithm", "gost")
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
			success = self.cipher.encrypt_decrypt_file(
				input_file, output_file, password, hash_algo, "yarrow160"
			)

			progress.update(task, completed=100)
		
		if success:
			try:
				with open(input_file, 'r', encoding='utf-8') as f:
					print(f"\nСодержимое файла для шифровки:\n{f.read()}")
			except:
				print("\n[dim]Невозможно показать содержимое исходного файла[/dim]")

			print("[green]Файл успешно зашифрован![/green]\n")
			try:
				with open (output_file, 'rb') as f:
					print(f"Результаты шифровки (первые 100 байт):\n{f.read(100)}")
			except:
				print("\n[dim]Невозможно показать содержимое зашифрованного файла[/dim]")
		else:
			print("[red]Ошибка при шифровании файла![/red]")
		
		Prompt.ask("\n[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def decrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Потоковое дешифрование файла [/bold blue]",
			style="blue"
		))

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

		password = Prompt.ask(
			"[bold yellow]Введите пароль для дешифрования[/bold yellow]",
			password=True
		)

		hash_algo = Prompt.ask(
			"[bold yellow]Выберите алгоритм хеширования[/bold yellow]",
			choices=["ready", "ma_prime", "gost"],
			default=self.config.get("default_hash_algirithm", "gost")
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
			task = progress.add_task("Дешифрование...", total=100)
			success = self.cipher.encrypt_decrypt_file(
				input_file, output_file, password, hash_algo, "yarrow160"
			)

			progress.update(task, completed=100)
		
		if success:
			print("\n[green]Файл успешно дешифрован![/green]")
			try:
				with open(output_file, "r", encoding='utf-8') as f:
					print(f"\nРезультат дешифровки:\n{f.read()}")
			except:
				print("\n[dim]Невозможно показать содержимое дешифрованного файла[/dim]")
			
		else:
			print("[red]Ошибка при дешифровании файла![/red]")
		
		Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def block_encrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold green] Блочное шифрование файла [/bold green]",
			style="green"
		))

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

		password = Prompt.ask(
			"[bold yellow]Введите пароль для шифрования[/bold yellow]",
			password=True
		)

		block_settings = self.config.get("block_cipher_settings", {})
		algorithm = block_settings.get("algorithm", "scrambler")
		block_size = block_settings.get("block_size", 7)

		if algorithm != "des":
			use_cbc = Prompt.ask(
				"[bold yellow]Использовать режим CBC?[/bold yellow]",
				choices=["y", "n"],
				default="y"
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
			task = progress.add_task("Блочное шифрование...", total=100)

			try:
				if algorithm == 'des':
					des_handler = DESHandler(password, "gost", "yarrow160")
					key1, key2, key3 = des_handler.generate_des_keys()
					cipher = DESEEE3(key1, key2, key3)
					
					progress.update(task, completed=33)

					with open(input_file, "rb") as f:
						data = f.read()
					
					encrypted_data = cipher.encrypt(data)

					progress.update(task, completed=66)

					with open(output_file, "wb") as f:
						f.write(encrypted_data)
					
					progress.update(task, completed=100)

					print(f"\n[cyan]Параметры шифрования:[/cyan]")
					print(f"Алгоритм: DES с схемой EEE3")
					print(f"Размер блока: 8 байт")
					print(f"Режим ECB")
					print(f"Ключ 1 (hex): {key1.hex()}")
					print(f"Ключ 2 (hex): {key2.hex()}")
					print(f"Ключ 3 (hex): {key3.hex()}")
					print(f"Алгоритм хеширования: gost")

				elif use_cbc == "y":
					cbc_scrambler = CBCScrambler(
						password=password,
						block_size=block_size,
						hash_algoritm="gost",
						generator_type="yarrow160"
					)

					progress.update(task, completed=33)

					with open(input_file, "rb") as f:
						data = f.read()
					
					encrypted_data = cbc_scrambler.encrypt(data)

					progress.update(task, completed=66)

					with open(output_file, "wb") as f:
						f.write(encrypted_data)
					
					progress.update(task, completed=100)

					print(f"\n[cyan]Параметры шифрования:[/cyan]")
					print(f"Алгоритм: {algorithm}")
					print("Режим: CBC")
					print(f"Размер блока: {block_size} байт")
					print(f"Сдвиг: {cbc_scrambler.scrambler.shift_bits} бит")
					print(f"Направление: {cbc_scrambler.scrambler.direction}")
					print(f"Алгоритм хеширования: gost")
					print(f"IV (hex): {cbc_scrambler.iv.hex()}")
				else:
					scrambler = Scrambler(
						password=password,
						block_size=block_size,
						hash_algorithm="gost",
						generator_type="yarrow160"
					)

					progress.update(task, completed=33)

					with open(input_file, "rb") as f:
						data = f.read()
					
					encrypted_data = scrambler.encrypt(data)

					progress.update(task, completed=66)

					with open(output_file, 'wb') as f:
						f.write(encrypted_data)
					
					progress.update(task, completed=100)

					print(f"\n[cyan]Параметры шифрования:[/cyan]")
					print(f"Алгоритм: {algorithm}")
					print(f"Размер блока: {block_size} байт")
					print(f"Сдвиг: {scrambler.shift_bits} бит")
					print(f"Направление: {scrambler.direction}")
					print(f"Алгоритм хеширования: gost")

					try:
						with open(input_file, 'r', encoding='utf-8') as f:
							original_content = f.read()
							print(f"Исходное содержимое (первые 200 символов):\n{original_content[:200]}...")
					except:
						print(f"\n[dim]Размер исходного файла: {len(data)} байт[/dim]")
				
				print("\n[green]Файл успешно зашифрован с использованием блочного шифра![/green]")
			
			except Exception as e:
				print(f"[red]Ошибка при блочном шифровании: {e}[/red]")
				progress.update(task, completed=100)

		Prompt.ask("\n[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")
	
	def block_decrypt_menu(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold blue] Блочное дешифрование файла [/bold blue]",
			style="green"
		))

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

		password = Prompt.ask(
			"[bold yellow]Введите пароль для дешифрования[/bold yellow]",
			password=True
		)

		block_settings = self.config.get("block_cipher_settings", {})
		algorithm = block_settings.get("algorithm", "scrambler")
		block_size = block_settings.get("block_size", 7)

		if algorithm != "des":
			use_cbc = Prompt.ask(
				"[bold yellow]Файл зашифрован в режиме CBC?[/bold yellow]",
				choices=["y", "n"],
				default="y"
			)

		self.config["output_file_path"] = output_file
		self._save_config()

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			BarColumn(),
			TaskProgressColumn(),
			transient=True,
		) as progress:
			task = progress.add_task("Блочное дешифрование...", total=100)

			try:
				if algorithm == "des":
					des_handler = DESHandler(password, "gost", "yarrow160")
					key1, key2, key3 = des_handler.generate_des_keys()
					cipher = DESEEE3(key1, key2, key3)

					progress.update(task, completed=33)

					with open(input_file, "rb") as f:
						encrypted_data = f.read()
					
					decrypted_data = cipher.decrypt(encrypted_data)

					progress.update(task, completed=66)

					with open(output_file, "wb") as f:
						f.write(decrypted_data)
					
					progress.update(task, completed=100)
				elif use_cbc == "y":
					cbc_scrambler = CBCScrambler(
						password=password,
						block_size=block_size,
						hash_algoritm="gost",
						generator_type="yarrow160"
					)

					progress.update(task, completed=33)

					with open(input_file, "rb") as f:
						encrypted_data = f.read()
					
					decrypted_data = cbc_scrambler.decrypt(encrypted_data)

					progress.update(task, completed=66)

					with open(output_file, "wb") as f:
						f.write(decrypted_data)
					
					progress.update(task, completed=100)

					print(f"\n[cyan]Параметры дешифрования:[/cyan]")
					print(f"Алгоритм: {algorithm}")
					print("Режим: CBC")
					print(f"Размер блока: {block_size} байт")
					print(f"Сдвиг: {cbc_scrambler.scrambler.shift_bits} бит")
					print(f"Направление: {cbc_scrambler.scrambler.direction}")
					print(f"Алгоритм хеширования: gost")
					print(f"IV (hex): {cbc_scrambler.iv.hex()}")
				else:
					scrambler = Scrambler(
						password=password,
						block_size=block_size,
						hash_algorithm="gost",
						generator_type="yarrow160"
					)

					progress.update(task, completed=33)

					with open(input_file, "rb") as f:
						encrypted_data = f.read()
					
					decrypted_data = scrambler.decrypt(encrypted_data)

					progress.update(task, completed=66)

					with open(output_file, 'wb') as f:
						f.write(decrypted_data)
					
					progress.update(task, completed=100)

					print(f"\n[cyan]Параметры дешифрования:[/cyan]")
					print(f"Алгоритм: {algorithm}")
					print(f"Размер блока: {block_size} байт")
					print(f"Сдвиг: {scrambler.shift_bits} бит")
					print(f"Направление: {scrambler.direction}")
					print(f"Алгоритм хеширования: gost")

				print("\n[green]Файл успешно дешифрован с использованием блочного шифра![/green]")

				try:
					with open(output_file, 'r', encoding='utf-8') as f:
						decrypted_content = f.read()
						print(f"\nДешифрованное содержимое:\n{decrypted_content}")
				except:
					print(f"\n[dim]Размер дешифрованного файла: {len(decrypted_data)} байт[/dim]")

			except Exception as e:
				print(f"[red]Ошибка при блочном дешифровании: {e}[/red]")
				progress.update(task, completed=100)

		Prompt.ask("\n[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")
	
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
			hash_algo,
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
			"• Потоковое шифрование и дешифрование файлов\n"
			"• Блочное шифрование и дешифрование файлов\n"
			"• Хеширование паролей с использованием различных алгоритмов\n"
			"• Использование различных генераторов псевдослучайных чисел\n\n"
			"[bold]Алгоритмы хеширования:[/bold]\n"
			"• [cyan]ready[/cyan] - готовая функция (SHA-256)\n"
			"• [cyan]ma_prime[/cyan] - собственная реализация MaPrime\n"
			"• [cyan]gost[/cyan] - собственная реализация ГОСТ Р 34.11-94\n\n"
			"[bold]Генераторы ПСЧ:[/bold]\n"
			"• [cyan]yarrow160[/cyan] - криптографический генератор Yarrow-160\n\n"
			"[bold]Блочные шифры:[/bold]"
			"• [cyan]Скремблирование (7 байт)[/cyan]\n"
			"• [cyan]Режим CBC[/cyan]\n"
			"• [cyan]DES (Режим ECB + схема DES-EEE3[/cyan]\n\n"
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
			"3. Настройки блочных шифров\n" \
			"4. Выход\n"
		)
		self.console.rule(style="blue")

		choice = Prompt.ask(
			"[bold yellow]Выберите пункт[/bold yellow]",
			choices=["1", "2", "3", "4"],
			default="1"
		)

		if choice == "1":
			self._file_path_settings()
		elif choice == "2":
			self._default_settings()
		elif choice == "3":
			self._block_cipher_settings()
	
	def _file_path_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print("Текущие настройки путей:")
		print(f"Входной файл: {self.config.get("input_file_path", "не указан")}")
		print(f"Выходной файл: {self.config.get('output_file_path', "не указан")}")
		self.console.rule(style="blue")

		print("1. Изменить путь до входного файла")
		print("2. Изменить путь до выходного файла")
		print("3. Очистить все пути")
		print("4. Назад")

		setting = Prompt.ask(
			"[bold yellow]Выберите настройку[/bold yellow]",
			choices=["1", "2", "3", "4"],
			default="1"
		)

		if setting == "1":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для входного файла[/bold yellow]")
			self.config["input_file_path"] = new_path
		elif setting == "2":
			new_path = Prompt.ask("[bold yellow]Введите новый путь для выходного файла[/bold yellow]")
			self.config["output_file_path"] = new_path
		elif setting == "3":
			self.config["input_file_path"] = ""
			self.config["output_file_path"] = ""
			print("[green]Все пути очищены[/green]")
		elif setting == "4":
			return

		self._save_config()	
		print("[green]Настройки сохранены![/green]")
		Prompt.ask("[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")
	
	def _default_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print("Текущие настройки по умолчанию:")
		print(f"Алгоритм хеширования: {self.config.get('default_hash_algirithm', 'gost')}")
		self.console.rule(style="blue")

		print("1. Изменить алгоритм хеширования по умолчанию")
		print("2. Назад")

		setting = Prompt.ask(
			"[bold yellow]Выберите настройку[/bold yellow]",
			choices=["1", "2"],
			default="1"
		)

		if setting == "1":
			new_algo = Prompt.ask(
				"[bold yellow]Выберите алгоритм хеширования по умолчанию[/bold yellow]",
				choices=["ready", "ma_prime", "gost"],
				default=self.config.get("default_hash_algorithm", "gost")	
			)
			self.config["default_hash_algorithm"] = new_algo
		elif setting == "2":
			return
			
		self._save_config()
		print("[green]Настройки сохранены![/green]")
		Prompt.ask("[bold yellow]Нажмите любую кнопку чтобы продолжить[/bold yellow]")
	
	def _block_cipher_settings(self) -> None:
		self.console.clear()
		self.console.rule(style="blue")

		print(Panel.fit(
			"[bold cyan] Настройки блочных шифров [/bold cyan]"
		))

		block_settings = self.config.get("block_cipher_settings", {})

		print("Текущие настройки блочных шифров:")
		print(f"Алгоритм: {block_settings.get('algorithm', 'scrambler')}")
		print(f"Режим: {block_settings.get('mode', 'cbc')}")
		print(f"Размер блока: {block_settings.get('block_size', 7)} байт")
		
		self.console.rule(style="blue")

		print("1. Изменить алгоритм")
		print("2. Изменить режим")
		print("3. Изменить размер блока")
		print("4. Назад")

		choice = Prompt.ask(
			"[bold yellow]Выберите настройку[/bold yellow]",
			choices=["1", "2", "3", "4"],
			default="1"
		)

		if choice == "1":
			new_algo = Prompt.ask(
				"[bold yellow]Выберите алгоритм блочного шифрования[/bold yellow]",
				choices=["scrambler", "des"],
				default=block_settings.get("algrorithm", "scrambler")
			)
			block_settings["algorithm"] = new_algo
		elif choice == "2":
			new_mode = Prompt.ask(
				"[bold yellow]Выберите режим работы[/bold yellow]",
				choices=["cbc", "no mode"],
				default=block_settings.get("mode", "cbc")
			)
			block_settings["mode"] = new_mode
		elif choice == "3":
			new_size = Prompt.ask(
				"[bold yellow]Введите размер блока (байт)[/bold yellow]",
				default=str(block_settings.get("block_size", 7))
			)
			block_settings["block_size"] = int(new_size)
		elif choice == "4":
			return

		self.config["block_cipher_settings"] = block_settings
		self._save_config()
		print("[green]Настройки блочных шифров сохранены[/green]")
		Prompt.ask("[bold yellow]Нажмите любую кнопку, чтобы продолжить[/bold yellow]")
	
	def main_loop(self) -> None:
		while True:
			self.print_title()
			self.print_menu()
	