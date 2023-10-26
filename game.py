from agent import Agent
from fractions import Fraction
import datetime



class Player:
    def __init__(self, agent, rounds, coins, opponents):
        self.agent = agent
        self.coins = coins
        self.score = Fraction(0)
        self.time_elapsed = datetime.timedelta(0)
        self.disqualified = False
        self.bid_history = []
    
        self.agent.write(f'{rounds} {coins} {opponents}')

    def bid(self):
        my_bid = self._bid()
        self.bid_history.append(my_bid)
        return my_bid

    def _bid(self):
        if self.disqualified:
            return -1

        bid = int(self.agent.read())
        if not 0 <= bid <= self.coins:
            self.disqualified = True
            return -1

        self.coins -= bid
        return bid

    def inform(self, bids):
        self.agent.write('\n'.join(map(str, bids)))

    def win(self, winners):
        self.score += Fraction(1, winners)


class Game:
    def __init__(self, paths, rounds=None, coins=None):
        # TODO: parallelize
        agents = [Agent(path) for path in paths]
        self.rounds = rounds or max(10**4, 10**6 // len(agents))
        self.coins = coins or 2 * self.rounds
        self.players = [
            Player(
                agent,
                self.rounds,
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
        return '\n'.join(','.join(map(str, player.bid_history)) for player in self.players)

if __name__ == '__main__':
    import logging
    logging.basicConfig(filename='game.log', level=logging.DEBUG)
    from glob import glob
    agents = glob('submissions/*.cpp') + glob('submissions/*.py') + glob('submissions/*.js')
    
    logging.log(logging.INFO, f'loaded agents {" ".join(agents)}')

    g = Game(agents)
    g.play()

    with open(f'results/{datetime.datetime.utcnow().replace(microsecond=0).isoformat()}.csv', 'w') as f:
        f.write(g.to_csv()+'\n')



    ranking = sorted(range(len(g.players)), key=lambda id: (g.players[id].score, g.players[id].coins), reverse=True)
    scoreboard = '\n'.join(f'{pos}.\t{id}\t{g.players[id].score}\t{g.players[id].coins}' for pos, id in enumerate(ranking, 1))
    print(scoreboard)


    