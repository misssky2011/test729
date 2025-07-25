import randomTest

# 定义纸牌的花色和点数
suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King", "Ace"]

# 定义纸牌类
class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"{self.rank} of {self.suit}"

# 定义牌堆类
class Deck:
    def __init__(self):
        self.cards = []
        for suit in suits:
            for rank in ranks:
                self.cards.append(Card(suit, rank))

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop()

# 定义手牌类，用于存储玩家或庄家手中的牌
class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = 0
        num_aces = 0
        for card in self.cards:
            rank = card.rank
            if rank in ["Jack", "Queen", "King"]:
                value += 10
            elif rank == "Ace":
                value += 11
                num_aces += 1
            else:
                value += int(rank)

        while value > 21 and num_aces > 0:
            value -= 10
            num_aces -= 1

        return value

# 定义玩家类
class Player:
    def __init__(self, name):
        self.name = name
        self.hand = Hand()

    def hit(self, deck):
        self.hand.add_card(deck.deal())

    def stand(self):
        pass

    def get_hand_value(self):
        return self.hand.get_value()

# 定义游戏主函数
def play_blackjack():
    print("欢迎来到21点游戏！")
    deck = Deck()
    deck.shuffle()

    player = Player("玩家")
    dealer = Player("庄家")

    # 初始发牌
    for _ in range(2):
        player.hit(deck)
        dealer.hit(deck)

    while True:
        print(f"{player.name} 的手牌：")
        for card in player.hand.cards:
            print(card)
        print(f"总点数：{player.get_hand_value()}")

        choice = input("要牌（h）还是停牌（s）？ ").lower()
        if choice == "h":
            player.hit(deck)
            if player.get_hand_value() > 21:
                print("爆牌了，你输了！")
                return
        elif choice == "s":
            break

    while dealer.get_hand_value() < 17:
        dealer.hit(deck)
        if dealer.get_hand_value() > 21:
            print("庄家爆牌了，你赢了！")
            return

    player_value = player.get_hand_value()
    dealer_value = dealer.get_hand_value()

    if player_value > dealer_value:
        print("你赢了！")
    elif player_value < dealer_value:
        print("你输了！")
    else:
        print("平局！")


if __name__ == "__main__":
    play_blackjack()