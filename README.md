# BTC Dip-Buy Bot — btc-race-24h-20261123-0511

Long-only, one position at a time, full size ($1,000 start). Buys a 30-minute
dip once the last 5 minutes turn positive, then exits at a fixed +1.2%
take-profit or a fixed −1.2% stop-loss, both measured against the close of the
bar on which the buy was decided.

## Strategy

- **Entry:** on a bar where the 30-minute return (close now vs close 30 bars
  ago) is below −0.8% AND the last 5-minute return (close now vs close 5 bars
  ago) is positive. Buy with the full cash balance. Only when flat, and only
  while cumulative realized losses are above −$15 (stops opening new positions
  once realized losses reach $15).
- **Exit:** sell the whole position when a bar's close reaches +1.2% (take
  profit) or −1.2% (stop loss) versus the entry bar's close.
- **Orders:** max slippage 100 bps (1%). Orders fill at the next bar's open.
- **Why the bounce confirmation:** a 30-minute dip alone keeps falling more
  often than it reverses, so the bot only buys once the last 5 minutes have
  turned up — that turn is the first sign the dip is a bounce rather than the
  start of a slide.

All arithmetic is integer (micro-USDC and integer prices); no floats, no
clock, no network, no files, no randomness. Two runs on the same bars produce
byte-identical replies.

## Dev-window result (1,440 one-minute bars, CBBTC)

- Net PnL: **+$17.66** (final cash $1,017.66)
- Trades: **4** (2 buys, 2 sells)
- Max drawdown: **0.59%**
- Determinism: two runs produce byte-identical replies (1,440 replies each)
- Dev gate (PnL > 0, ≥1 trade, drawdown ≤ 25%): **PASS**

## Files

- `main.py` — the bot (stdlib only, speaks agent-fun/bars-replay/v1).
- `vendor/makefun_bars.py` — the kit's Python SDK shim, copied byte-for-byte.
