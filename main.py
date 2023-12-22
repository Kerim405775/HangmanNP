import pygame
import random
from hangman_words import word_list

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game")

# Kolory
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Fonty
LETTER_FONT = pygame.font.SysFont('comicsans', 40)
WORD_FONT = pygame.font.SysFont('comicsans', 60)
TITLE_FONT = pygame.font.SysFont('comicsans', 70)

# Wczytanie obrazków do wyświetlania stanów gry
hangman_images = [pygame.image.load(f'hangman{i}.png') for i in range(6, -1, -1)]

def draw_message(message, font, color, y):
    text = font.render(message, 1, color)
    win.blit(text, (WIDTH/2 - text.get_width()/2, y))

def input_player_name():
    input_box = pygame.Rect(WIDTH/2 - 100, HEIGHT/2 - 50, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    font = pygame.font.Font(None, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        win.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_box.w = width
        win.blit(txt_surface, (input_box.x+5, input_box.y+5))
        pygame.draw.rect(win, color, input_box, 2)
        pygame.display.flip()

def draw_menu():
    win.fill(WHITE)
    title = TITLE_FONT.render("Hangman Game", 1, BLACK)
    win.blit(title, (WIDTH/2 - title.get_width()/2, 100))

    start_text = LETTER_FONT.render("Press 1 to Start", 1, BLACK)
    win.blit(start_text, (WIDTH/2 - start_text.get_width()/2, 300))

    ranking_text = LETTER_FONT.render("Press 2 for Ranking", 1, BLACK)
    win.blit(ranking_text, (WIDTH/2 - ranking_text.get_width()/2, 350))

    quit_text = LETTER_FONT.render("Press 3 to Quit", 1, BLACK)
    win.blit(quit_text, (WIDTH/2 - quit_text.get_width()/2, 400))

    pygame.display.update()

def draw_ranking(ranking):
    win.fill(WHITE)
    title = TITLE_FONT.render("Ranking", 1, BLACK)
    win.blit(title, (WIDTH/2 - title.get_width()/2, 50))

    y = 150
    for rank, entry in enumerate(ranking, start=1):
        text = LETTER_FONT.render(f"{rank}. {entry[0]} - Lives: {entry[1]}", 1, BLACK)
        win.blit(text, (WIDTH/2 - text.get_width()/2, y))
        y += 50

    back_text = LETTER_FONT.render("Press B to Back", 1, BLACK)
    win.blit(back_text, (WIDTH/2 - back_text.get_width()/2, 500))

    pygame.display.update()

def save_score(player_name, score):
    with open("hangman_ranking.txt", "a") as file:
        file.write(f"{player_name},{score}\n")

def load_ranking():
    try:
        with open("hangman_ranking.txt", "r") as file:
            lines = file.readlines()
            ranking = [line.strip().split(",") for line in lines]
            ranking = [(entry[0], int(entry[1])) for entry in ranking]
            ranking.sort(key=lambda x: x[1], reverse=True)
            return ranking
    except FileNotFoundError:
        return []

def draw_game(chosen_word, guessed_letters, lives):
    win.fill(WHITE)
    # Rysowanie słowa
    display_word = ""
    for letter in chosen_word:
        if letter in guessed_letters:
            display_word += letter + " "
        else:
            display_word += "_ "
    text = WORD_FONT.render(display_word, 1, BLACK)
    win.blit(text, (WIDTH/2 - text.get_width()/2, 200))

    # Rysowanie liter
    start_x = 50
    start_y = 400
    gap = 40
    for i in range(26):
        x = start_x + gap * (i % 13)
        y = start_y + gap * (i // 13)
        letter = chr(65 + i)
        text = LETTER_FONT.render(letter, 1, BLACK)
        if letter.lower() in guessed_letters:
            pygame.draw.circle(win, RED, (x, y), 20, 3)
        else:
            pygame.draw.circle(win, BLACK, (x, y), 20, 3)
        win.blit(text, (x - text.get_width()/2, y - text.get_height()/2))

    # Wyświetlanie stanu zawieszenia
    win.blit(hangman_images[lives], (150, 100))

    pygame.display.update()

def main_menu():
    draw_menu()
    player_name = None
    entering_name = False  # Dodana zmienna kontrolująca wprowadzanie nazwy gracza

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    entering_name = True  # Rozpoczęcie wyboru opcji gracza lub gry jako gość
                elif event.key == pygame.K_a:
                    player_name = input_player_name()  # Wybór wprowadzenia nazwy gracza
                    start_game(player_name, is_guest=False)  # Rozpoczęcie gry z wybraną nazwą gracza
                elif event.key == pygame.K_b:
                    start_game("Guest", is_guest=True)  # Rozpoczęcie gry jako gość
                elif event.key == pygame.K_2:  # Dodajemy tę linię
                    ranking = load_ranking()  # Dodajemy tę linię
                    draw_ranking(ranking)  # Dodajemy tę linię
                    wait_for_back()  # Dodajemy tę linię
                elif event.key == pygame.K_3:  # Dodajemy tę linię
                    pygame.quit()  # Dodajemy tę linię
                    quit()  # Dodajemy tę linię

            if entering_name:  # Obsługa wyboru opcji gracza lub gry jako gość
                draw_name_menu()  # Rysowanie ekranu z opcjami
                entering_name = False  # Zakończenie wyboru opcji gracza lub gry jako gość

        pygame.display.update()

def draw_name_menu():
    win.fill(WHITE)
    title = TITLE_FONT.render("Enter Your Name", 1, BLACK)
    win.blit(title, (WIDTH / 2 - title.get_width() / 2, 100))

    title = TITLE_FONT.render("or Play as Guest", 1, BLACK)
    win.blit(title, (WIDTH / 2 - title.get_width() / 2, 160))

    name_option = LETTER_FONT.render("Press A for Name", 1, BLACK)
    win.blit(name_option, (WIDTH/2 - name_option.get_width()/2, 300))

    guest_option = LETTER_FONT.render("Press B for Guest", 1, BLACK)
    win.blit(guest_option, (WIDTH/2 - guest_option.get_width()/2, 350))

    pygame.display.update()

def wait_for_back():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_b:
                    draw_menu()
                    return

def letter_clicked(mouse_x, mouse_y):
    start_x = 50
    start_y = 400
    gap = 40
    for i in range(26):
        x = start_x + gap * (i % 13)
        y = start_y + gap * (i // 13)
        if x - 20 < mouse_x < x + 20 and y - 20 < mouse_y < y + 20:
            return chr(65 + i)
    return None

def start_game(player_name, is_guest=False):
    chosen_word = random.choice(word_list)
    lives = 6
    guessed_letters = []

    clock = pygame.time.Clock()
    run = True
    game_over = False

    while run:
        clock.tick(60)
        draw_game(chosen_word, guessed_letters, lives)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                letter = letter_clicked(mouse_x, mouse_y)
                if letter and letter.lower() not in guessed_letters:
                    guessed_letters.append(letter.lower())
                    if letter.lower() not in chosen_word:
                        lives -= 1

        # Sprawdzenie warunków wygranej/przegranej gry
        won = all(letter in guessed_letters for letter in chosen_word)
        if won:
            draw_game(chosen_word, guessed_letters, lives)  # Dodajemy tę linię
            draw_message("You win!", TITLE_FONT, BLACK, 50)
            pygame.display.update()
            pygame.time.wait(3000)
            game_over = True
        if lives == 0:
            draw_message("You lose!", TITLE_FONT, BLACK, 50)
            pygame.display.update()
            pygame.time.wait(3000)
            game_over = True

        if game_over:
            break

    # Zapis wyniku (jeśli gracz nie jest gościem i gra nie jest zakończona)
    if not is_guest and game_over:
        score = lives * len(chosen_word)  # Obliczanie punktów
        save_score(player_name, score)
    main_menu()  # Powrót do menu głównego

if __name__ == "__main__":
    main_menu()
