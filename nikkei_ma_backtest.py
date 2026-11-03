"""日経平均: 移動平均線 -5% で買い、+5% で売る を繰り返した場合の過去5年リターン。

使い方:  pip install yfinance pandas && python nikkei_ma_backtest.py [MA日数]
"""
import sys
import yfinance as yf

MA = int(sys.argv[1]) if len(sys.argv) > 1 else 25  # 既定は25日線
BUY, SELL = -0.05, 0.05

df = yf.download("^N225", period="6y", auto_adjust=False, progress=False)
close = df["Close"].squeeze().dropna()
ma = close.rolling(MA).mean()
start = close.index[-1] - __import__("pandas").DateOffset(years=5)
close, ma = close[close.index >= start], ma[ma.index >= start]

cash, pos, entry, trades = 1.0, False, 0.0, []
for d, p in close.items():
    dev = p / ma[d] - 1
    if not pos and dev <= BUY:
        pos, entry, buy_d = True, p, d
    elif pos and dev >= SELL:
        cash *= p / entry
        trades.append((buy_d.date(), entry, d.date(), p, p / entry - 1))
        pos = False

final = cash * (close.iloc[-1] / entry) if pos else cash
for t in trades:
    print(f"買 {t[0]} {t[1]:,.0f} → 売 {t[2]} {t[3]:,.0f}  {t[4]:+.2%}")
if pos:
    print(f"保有中: 買 {buy_d.date()} {entry:,.0f} (現在 {close.iloc[-1]:,.0f})")
print(f"\n{MA}日線 / 期間 {close.index[0].date()}〜{close.index[-1].date()}")
print(f"戦略リターン: {final - 1:+.2%}  (売買 {len(trades)} 回)")
print(f"買い持ち    : {close.iloc[-1] / close.iloc[0] - 1:+.2%}")
