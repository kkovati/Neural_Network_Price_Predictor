from plotly.graph_objects import Candlestick, Figure
from plotly.offline import plot
from datetime import datetime


def plot_candlestick(single_input):
    
    open_ = single_input[:,0]
    high_ = single_input[:,1]
    low_ = single_input[:,2]
    close_ = single_input[:,3]

    dates = list(range(single_input.shape[0]))
    
    fig = Figure(data=[Candlestick(x=dates,open=open_, high=high_, low=low_, 
                                   close=close_)])
    
    plot(fig)


#DELETE!!!!!!
def plot_example(input_set):

    open_data = [33.0, 33.3, 33.5, 33.0, 34.1]
    high_data = [33.1, 33.3, 33.6, 33.2, 34.8]
    low_data = [32.7, 32.7, 32.8, 32.6, 32.8]
    close_data = [33.05, 32.9, 33.3, 33.1, 33.1]
    dates = [datetime(year=2013, month=10, day=10),
             datetime(year=2013, month=11, day=10),
             datetime(year=2013, month=12, day=10),
             datetime(year=2014, month=1, day=10),
             datetime(year=2014, month=2, day=10)]
    
    dates = list(range(5))
    
    fig = Figure(data=[Candlestick(x=dates,open=open_data, high=high_data,
                                   low=low_data, close=close_data)])
    
    plot(fig)