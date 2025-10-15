import random


# Начальная раскладка кард (по 2 на руки юзеру и дилеру)
def start_layout() -> tuple[list[dict], list, dict]:
    deck = {'пики' : ['два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять', 'валет', 'дама', 'король', 'туз'],
            'червы': ['два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять', 'валет', 'дама', 'король', 'туз'],
            'крести': ['два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять', 'валет', 'дама', 'король', 'туз'],
            'бубны': ['два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять', 'десять', 'валет', 'дама', 'король', 'туз']}

    suits = {0: 'пики', 1: 'червы', 2: 'крести', 3: 'бубны'}

    dealer_deck = []
    for _ in range(2):
        suit = suits[random.randrange(4)]
        num = deck[suit].pop(random.randrange(len(deck[suit])))
        dealer_deck.append({num: suit})

    user_deck = []
    for _ in range(2):
        suit = suits[random.randrange(4)]
        num = deck[suit].pop(random.randrange(len(deck[suit])))
        user_deck.append({num: suit})

    return dealer_deck, user_deck, deck


# Чтение колоды на руках. При first_dealer = True показывается только одна карта. Вторая замазывается.
def read_arm(user_deck, first_dealer=False) -> str:
    message = []
    if not first_dealer:
        for card in user_deck:
            for num, suit in card.items():
                message.append(f"{num.title()} {suit}\n")
    else:
        for num, suit in user_deck[0].items():
            message.append(f"{num.title()} {suit}\n")
        message.append(f"{'*' * 5} {'*' * 5}\n")
    return ''.join(message)


# Подсчитывает сумму очков на руках
def count_points(user_deck):
    count = 0
    ace_count = 0 # Делаем подсчет тузов
    points = {'два': 2, 'три': 3, 'четыре': 4, 'пять': 5, 'шесть': 6, 'семь': 7, 'восемь': 8, 'девять': 9, 'десять': 10,
              'валет': 10, 'дама': 10, 'король': 10}
    for card in user_deck:
        for num in card:
            if num in points:
                count += points[num]
            else:
                ace_count += 1

    if count + ace_count >= 21:
        return count + ace_count
    else:
        n = ace_count
        for _ in range(n):
            ace_count -= 1
            if count + 11 + ace_count == 21:
                return count + 11 + ace_count
            elif count + 11 + ace_count > 21:
                return count + ace_count + 1
            else:
                count += 1
    return count



# добавляем карту пользователю. Отсутствует проверка на колоду.
def more_card(user_deck, deck):
    suits = {0: 'пики', 1: 'червы', 2: 'крести', 3: 'бубны'}
    suit = suits[random.randrange(4)]
    num = deck[suit].pop(random.randrange(len(deck[suit])))
    user_deck.append({num: suit})
    return user_deck, deck
