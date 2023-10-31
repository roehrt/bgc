import random
import time

n = int(input())
coins = 10**5
rounds = 10**3

other_bids = [0]*n

for round in range(rounds):
    my_bid = random.randint(0, coins)
    coins -= my_bid
    print(my_bid, flush=True)
    
    other_bids = [int(x) for x in input().split()]