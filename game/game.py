from agent import Agent
from fractions import Fraction
import datetime


class Player:
    def __init__(self, agent, coins, opponents):
        self.agent = agent
        self.coins = coins
        self.points = Fraction(0)
        self.rounds_disqualified = 0
        self.disqualified = False
        self.bid_history = []
        self.buffer = str(opponents)

    def bid(self):
        my_bid = self._bid()
        self.bid_history.append(my_bid)
        return my_bid

    def _bid(self):
        if self.disqualified:
            self.rounds_disqualified += 1
            return -1

        self.agent.resume()
        self.agent.write(self.buffer)
        bid = int(self.agent.read())
        self.agent.pause()

        if not 0 <= bid <= self.coins:
            self.disqualified = True
            self.agent.kill()
            self.rounds_disqualified += 1
            return -1

        self.coins -= bid
        return bid

    def inform(self, bids):
        self.buffer = "\n".join(map(str, bids))

    def score(self):
        return (self.points, -self.rounds_disqualified, self.coins)

    @property
    def name(self):
        return self.agent.name

    def win(self, winners):
        self.points += Fraction(1, winners)


class Game:
    def __init__(self, submissions, rounds=10**3, coins=10**5):
        agents = [Agent(sid) for sid in submissions]
        self.rounds = rounds
        self.coins = coins
        self.players = [
            Player(
                agent,
                self.coins,
                len(agents) - 1,
            )
            for agent in agents
        ]

    def play(self):
        for round in range(self.rounds):
            self.play_round()

    def play_round(self):
        # TODO: parallelize
        bids = [player.bid() for player in self.players]
        highest = max(bids)
        winners = sum(bid == highest for bid in bids)
        for player, bid in zip(self.players, bids):
            if bid == highest:
                player.win(winners)

        for id, player in enumerate(self.players):
            other_bids = bids[:id] + bids[id + 1 :]
            player.inform(other_bids)

    def to_csv(self):
        return "\n".join(
            ",".join(map(str, [player.name]+player.bid_history)) for player in self.players
        )


if __name__ == "__main__":
    from pathlib import Path
    submissions = [x.parts[-1] for x in Path("/submissions").iterdir() if x.is_dir()]
    
    g = Game(submissions)
    g.play()

    print(g.to_csv())

    ranking = sorted(
        range(len(g.players)),
        key=lambda id: g.players[id].score(),
        reverse=True,
    )
    scoreboard = "\n".join(
        f"{pos}.\t{g.players[id].name}\t{g.players[id].points}"
        for pos, id in enumerate(ranking, 1)
    )
    print(scoreboard)