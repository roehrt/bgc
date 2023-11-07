#include <bits/stdc++.h>
using namespace std;

int main() {
    cin.tie(0)->sync_with_stdio(0);
    int n; cin >> n;
    int coins = 1e5, rounds = 1e3;
    vector<int> other_bids(n);
    for (int round = 0; round < rounds; round++) {
        int my_bid = clamp(
            *max_element(other_bids.begin(), other_bids.end()),
            0,
            coins
        );
        coins -= my_bid;
        cout << my_bid << endl;
        for (int &bid : other_bids) cin >> bid;
    }
}