def save_score(client_port, score):
    """Zapisuje wynik gracza do pliku rankingowego."""
    with open('ranking.txt', 'a') as file:
        file.write(f'{client_port},{score}\n')

def get_scores():
    """Pobiera wyniki z pliku rankingowego i zwraca je jako listę tupli."""
    with open('ranking.txt', 'r') as file:
        lines = file.readlines()
    scores = []
    for line in lines:
        parts = line.strip().split(',')
        if len(parts) >= 2:
            player_info, score = parts[0], parts[-1]
            try:
                score = int(score)
                scores.append((player_info, score))
            except ValueError:
                print(f"Niepoprawny format punktów w linii: {line.strip()}")
        else:
            print(f"Niepoprawna linia w pliku rankingowym: {line.strip()}")
    return scores

def print_ranking():
    """Wypisuje ranking na podstawie wyników w pliku rankingowym i zwraca jako string."""
    scores = get_scores()
    scores.sort(key=lambda x: x[1], reverse=True)
    ranking_string = "\n".join(f"{player_name}: {score}" for player_name, score in scores)
    return ranking_string
