from fractions import Fraction
import argparse
import tabulate
import collections
import csv
import itertools
import io
import dominate.tags as t

argparser = argparse.ArgumentParser(description="Analyse index.md")
argparser.add_argument(
    "--set", help="Set to analyse", type=argparse.FileType("r"), nargs="+", required=True
)
argparser.add_argument("--rounds", help="Number of rounds", type=int, default=10**3)
argparser.add_argument("--summary", help="summary output", action="store_true")
g = argparser.add_mutually_exclusive_group()
g.add_argument("--html", help="HTML output", action="store_true")
g.add_argument("--web", help="Web output", action="store_true")

args = argparser.parse_args()


class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.coins_left = 10**5
        self.rounds_disqualified = 0
        self.bid_history = []

    def bid(self, amount):
        self.bid_history.append(amount)
        if amount == -1:
            self.rounds_disqualified += 1
            return
        self.coins_left -= amount

    def win(self, winners):
        self.points += Fraction(1, winners)

    def score(self):
        return (self.points, -self.rounds_disqualified, self.coins_left)

class CombinedPlayer:
    def __init__(self, players):
        self.players = players
        self.name = self.players[0].name

    @property
    def bid_history(self):
        return [bid for player in self.players for bid in player.bid_history]

    @property
    def points(self):
        return sum(player.points for player in self.players)

    @property
    def coins_left(self):
        return sum(player.coins_left for player in self.players)

    @property
    def rounds_disqualified(self):
        return sum(player.rounds_disqualified for player in self.players)

    def score(self):
        return (self.points, -self.rounds_disqualified, self.coins_left)

class Scoreboard:
    def __init__(self, players):
        self.players = sorted(players, key=lambda p: p.score(), reverse=True)

    @classmethod
    def from_csv(cls, f):
        reader = csv.reader(f)
        next(reader)
        rows = list(reader)
        players = [Player(row[0]) for row in rows]
        for round in range(1, args.rounds + 1):
            bids = [int(row[round]) for row in rows]
            highest = max(bids)
            for player, bid in zip(players, bids):
                player.bid(bid)
            if highest < 0:
                continue
            winners = sum(bid == highest for bid in bids)
            for player, bid in zip(players, bids):
                if bid == highest:
                    player.win(winners)

        return cls(players)

    def table_header(self, summary=False):
        return ["team name", "points", "rounds disqualified", "coins left"] + (
            list(map(str, range(1, args.rounds + 1))) if not summary else []
        )

    def table_data(self, summary=False):
        data = [
            [player.name, player.points, player.rounds_disqualified, player.coins_left]
            for player in self.players
        ]
        if not summary:
            for row, player in zip(data, self.players):
                row += player.bid_history
        return data

    def __str__(self):
        return self.table(summary=True)

    def table(self, summary=False, html=False):
        return tabulate.tabulate(
            self.table_data(summary=summary),
            headers=self.table_header(summary=summary),
            tablefmt="html" if html else "github",
            showindex=False if html else range(1, len(self.players) + 1),
        )

class CombinedScoreboard:
    def __init__(self, scoreboards):
        self.scoreboards = scoreboards
        self.players = collections.defaultdict(list)
        for scoreboard in scoreboards:
            for player in scoreboard.players:
                self.players[player.name].append(player)
        self.players = [CombinedPlayer(players) for players in self.players.values()]
        self.players = sorted(self.players, key=lambda p: p.score(), reverse=True)

    def table_header(self, summary=False):
        columns = ["team name", "points", "rounds disqualified", "coins left"]
        if not summary:
            rounds = [f'{run}.{_round}' for run, _round in
                itertools.product
                (
                    range(1, len(self.scoreboards) + 1),
                    range(1, args.rounds + 1),
                )
            ]
            columns += rounds
        return columns

    def table_data(self, summary=False):
        data = [
            [player.name, player.points, player.rounds_disqualified, player.coins_left]
            for player in self.players
        ]
        if not summary:
            for row, player in zip(data, self.players):
                row += player.bid_history
        return data

    def __str__(self):
        return self.table(summary=True)

    def table(self, summary=False, html=False):
        return tabulate.tabulate(
            self.table_data(summary=summary),
            headers=self.table_header(summary=summary),
            tablefmt="html" if html else "github",
            showindex=False if html else range(1, len(self.players) + 1),
        )

    def to_csv(self):
        result = io.StringIO()
        writer = csv.writer(result)
        writer.writerow(self.table_header())
        writer.writerows(self.table_data())
        return result.getvalue()

    def web(self, summary=False):
        if summary:
            return self.table(summary=True, html=True)
        highest = [None]*4+[max(col) for col in zip(*[player.bid_history for player in self.players])]
        doc = t.div()
        with doc:
            with t.table():
                with t.thead():
                    t.tr([t.th(col) for col in self.table_header()])
                with t.tbody():
                    for row in self.table_data():
                        with t.tr():
                            for i, col in enumerate(row):
                                if isinstance(col, Fraction):
                                    col = float(col)
                                with t.td(col):
                                    if col == -1:
                                        t.attr(data_disqualified="true")
                                    elif col == highest[i]:
                                        t.attr(data_highest="true")
            csv_data = self.to_csv()
            download_size = round(len(csv_data.encode("utf-8")) / 1024)
            t.a(
                f"Download raw data (csv, {download_size} kB)",
                href="data:text/csv;charset=utf-8,"+csv_data,
                download="data.csv"
            )
        return doc.render(pretty=False)





if len(args.set) > 1:
    s = CombinedScoreboard([Scoreboard.from_csv(f) for f in args.set])
else:
    s = Scoreboard.from_csv(args.set[0])
if args.web:
    print(s.web(summary=args.summary))
else:
    print(s.table(summary=args.summary, html=args.html))
