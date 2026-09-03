import mplfinance as mpf

def plot(df, signals, title=None, save=False, filename=None):

    plot_data = df[["open", "high", "low", "close"]].copy()
    plot_data.index.name = "Date"

    addplots = []
    panel_map = {"price": 0}
    next_panel = 1

    for signal in signals:

        panel = signal.plot_panel

        if panel == "price":
            panel_number = 0
        else:
            if panel not in panel_map:
                panel_map[panel] = next_panel
                next_panel += 1

            panel_number = panel_map[panel]

        addplots.extend(signal.plot(df, panel_number))

    ratios = [8] + [1.5] * (next_panel - 1)

    fig, axes = mpf.plot(plot_data, type="candle", style="binance",
        title=title or "", ylabel="Price",
        addplot=addplots, panel_ratios=ratios, volume=False,
        figratio=(10, 7), figscale=2.0, returnfig=True)

    mpf.show()

    if save:
        fig.savefig(filename or "chart.png")