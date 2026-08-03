"""Paired bootstrap comparisons and tier assignment over a results JSON.

Usage: python3 stats.py results/v31/results-v31-OFFICIAL.json "Legibility Sans" Verdana
       python3 stats.py results/v31/results-v31-OFFICIAL.json --tiers
"""
import json, random, sys

def paired(res, conds, a, b, n_boot=6000, seed=42):
    diffs = []
    for c in conds:
        for x, y in zip(res[a]['cells'][c]['reps'], res[b]['cells'][c]['reps']):
            diffs.append(x - y)
    rnd = random.Random(seed)
    n = len(diffs)
    boots = sorted(sum(diffs[rnd.randrange(n)] for _ in range(n)) / n
                   for _ in range(n_boot))
    return (sum(diffs) / n * 100,
            boots[int(n_boot * 0.025)] * 100, boots[int(n_boot * 0.975)] * 100)

def main():
    data = json.load(open(sys.argv[1]))
    res, conds = data['results'], data['conditions']
    if sys.argv[2] == '--tiers':
        leader = max(res, key=lambda f: res[f]['grand_mean'])
        print(f'leader: {leader}')
        for f in sorted(res, key=lambda f: -res[f]['grand_mean']):
            if f == leader:
                print(f'  T1  {f}')
                continue
            _, lo, hi = paired(res, conds, f, leader)
            print(f"  {'T1 ' if hi >= 0 else '    '} {f:28s} [{lo:+.2f},{hi:+.2f}]")
        return
    m, lo, hi = paired(res, conds, sys.argv[2], sys.argv[3])
    verdict = 'AHEAD' if lo > 0 else ('BEHIND' if hi < 0 else 'TIE')
    print(f'{sys.argv[2]} vs {sys.argv[3]}: {m:+.2f}pt, 95% CI [{lo:+.2f}, {hi:+.2f}] -> {verdict}')

if __name__ == '__main__':
    main()
