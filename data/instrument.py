from tvDatafeed import TvDatafeed, Interval

class instrument:
    '''
    This gets the OHLC data from Trading View. 
    Input:
        symbol (str)
        sym_exchange (str)
        timeframe (str: 'W', 'D', '4H')
        n_bars (int)
    Output
        data (dataframe)
    '''
    def __init__(self, symbol, sym_exchange, timeframe='W', n_bars=150):
        '''
        '''
        self.symbol = symbol
        self.sym_exchange = sym_exchange
        self.timeframe = timeframe
        self.n_bars = n_bars
        
        self.check_input()
        self.get_ohlc_data()
        
    def check_input(self):
        '''
        '''
        match self.timeframe:
            case 'W':
                self.interval = Interval.in_weekly
            case 'D':
                self.interval = Interval.in_daily
            case '4H':
                self.interval = Interval.in_4_hour
            case _:
                raise ValueError("Timeframe Input not valid: 'W', 'D', '4H'.")
        
        if not isinstance(self.n_bars, int):
            raise ValueError("n_bars is not of type int")
            
    def get_ohlc_data(self):
        '''
        '''
        tv = TvDatafeed()
        self.data = tv.get_hist(
            symbol=self.symbol,
            exchange=self.sym_exchange,
            interval=self.interval,
            n_bars=self.n_bars
        )
        return self