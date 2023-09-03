import flet as ft
from copy import deepcopy
from time import sleep
from game import Game


# Possible Refactors - "Grid" class to move all grid update functions and the share function to one place.

ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
COLORS = {"green": "0x4E8D53", "yellow": "0xB5A33B", "grey": "0x3C3A3A", "transparent": None}


def create_empty_row():
	squares = []
	
	for _ in range(5):
		letter_space = ft.Text("", weight = ft.FontWeight.W_700, size = 30)
		
		grid_square = ft.Container(
			letter_space, border = ft.border.all(2, ft.colors.GREY_600),
			width = 60,
			height = 60,
			alignment = ft.alignment.center,
			padding = ft.padding.only(bottom = 5)
		)
		
		squares.append(grid_square)
	
	return ft.Row(squares, alignment = ft.MainAxisAlignment.CENTER)


def main(page: ft.Page):
	def snack_alert(text: str):
		page.snack_bar = ft.SnackBar(
			ft.Text(text, color = ft.colors.WHITE, text_align = ft.TextAlign.CENTER),
			bgcolor = ft.colors.GREY_700,
			behavior = ft.SnackBarBehavior.FLOATING,
			width = 300,
			duration = 2000
		)
		page.snack_bar.open = True
		page.update()
	
	def update_grid_colors(colors: list[str]):
		nonlocal ongoing_animation
		
		ongoing_animation = True
		
		for i, tile in enumerate(grid.controls[wordle.current_row].controls):
			tile.bgcolor = COLORS[colors[i]]
			sleep(0.3)
			page.update()
			
		ongoing_animation = False
	
	def finish(victory: bool):
		nonlocal ongoing_animation
		
		ongoing_animation = True
		
		def replay(e):
			dialog.open = False
			page.update()
			play_again()
		
		def share(e):
			page.set_clipboard(get_share_string())
			snack_alert("Copied!")
		
		dialog = ft.AlertDialog(
			modal = True,
			title = ft.Text("Congrats! 🎉" if victory else "Nice Try :(", text_align=ft.TextAlign.CENTER),
			content = None if victory else ft.Text(f'The word was {wordle.solution.upper()}.', text_align = ft.TextAlign.CENTER),
			actions = [
				ft.TextButton("Play Again", on_click = replay),
				ft.TextButton("Share", on_click = share),
				ft.TextButton(content = ft.Text("Exit", color = ft.colors.RED), on_click = lambda e: page.window_close())
			],
			actions_alignment = ft.MainAxisAlignment.CENTER
		)
		
		page.dialog = dialog
		dialog.open = True
		page.update()
		
	def update_grid():
		for i, space in enumerate(wordle.grid[wordle.current_row]):
			grid.controls[wordle.current_row].controls[i].content.value = space
	
	def clear_grid():
		for x in range(6):
			for i in range(5):
				grid.controls[x].controls[i].content.value = ""
				grid.controls[x].controls[i].bgcolor = COLORS["transparent"]
	
	def play_again():
		nonlocal ongoing_animation
		
		wordle.start_new_game()
		clear_grid()
		print(f'Solution is: {wordle.solution}')
		ongoing_animation = False
		page.update()
	
	def submit_word():
		colors = wordle.submit_word()
		
		if colors:
			update_grid_colors(colors)
			wordle.current_row += 1
			
			if colors == ["green"] * 5:
				sleep(0.5)
				finish(True)
			
			elif wordle.current_row == 6:
				sleep(0.5)
				finish(False)
		
		else:
			snack_alert("Invalid Word!")

	def build_keyboard():
		# These callbacks are kinda scuffed because they work inconsistently (especially with submit_word()). dont like
		
		def enter_callback(e):
			submit_word()
			page.update()
		
		enter_button = ft.IconButton(
			icon = ft.icons.CHECK,
			icon_color = ft.colors.WHITE,
			on_click = enter_callback
		)
		
		def remove_callback(e):
			wordle.remove_letter()
			update_grid()
			page.update()
		
		backspace_button = ft.IconButton(
			icon = ft.icons.BACKSPACE_OUTLINED,
			icon_color = ft.colors.WHITE,
			on_click = remove_callback
		)
		
		letter_buttons = []
		for i in range(26):
			button = ft.TextButton(ALPHABET[i], style = ft.ButtonStyle(shape = ft.RoundedRectangleBorder(radius = 0)))
			
			def letter_callback(e):
				wordle.enter_letter(e.control.text)
				update_grid()
				page.update()
			
			button.on_click = letter_callback
			
			letter_buttons.append(button)
		
		buttons = [*letter_buttons, backspace_button, enter_button]
		
		return ft.Column([
			ft.Row(buttons[:14], alignment = ft.MainAxisAlignment.CENTER),
			ft.Row(buttons[14:], alignment = ft.MainAxisAlignment.CENTER)
		])
	
	def get_share_string():
		share = [["" for _ in range(5)] for _ in range(6)]
		
		for x in range(6):
			for i, tile in enumerate(grid.controls[x].controls):
				if tile.bgcolor == COLORS["green"]:
					share[x][i] = "🟩"
				elif tile.bgcolor == COLORS["yellow"]:
					share[x][i] = "🟨"
				elif tile.bgcolor == COLORS["grey"]:
					share[x][i] = "⬛"
		
		return "Wyrdle Unlimited\n\n" + "\n".join(["".join(share[i]) for i in range(5)]).strip()
	
	def handle_input(e: ft.KeyboardEvent):
		# Do nothing if a modifier key is held down or if an animation is playing.
		if any([e.shift, e.ctrl, e.alt, e.meta, ongoing_animation]):
			return
		
		match e.key:
			case e.key if e.key in ALPHABET:
				wordle.enter_letter(e.key)
				update_grid()
				page.update()
			
			case "Backspace":
				wordle.remove_letter()
				update_grid()
				page.update()
				
			case "Enter":
				submit_word()
				page.update()
				
	page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
	page.on_keyboard_event = handle_input
	page.fonts = {"Helvetica": "https://github.com/ifvictr/helvetica-neue/blob/master/HelveticaNeue-Bold.otf"}
	page.theme = ft.Theme(font_family = "Helvetica")
	page.title = "Wyrdle"
	
	title = ft.Text("Wyrdle Unlimited", size = 70, font_family = "Helvetica")
	grid = ft.Column([create_empty_row() for _ in range(6)])
	ongoing_animation = False
	wordle = Game()
	print(f'Solution is: {wordle.solution}')
	
	page.add(title)
	page.add(ft.Text("A Wordle clone by Kingston V.", size = 12, italic = True))
	page.add(ft.Divider())
	page.add(grid)
	page.add(build_keyboard())


ft.app(target=main)
