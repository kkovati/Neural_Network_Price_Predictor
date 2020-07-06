import csv
from copy import deepcopy
from datetime import datetime
import numpy as np
from plotly.graph_objects import Candlestick, Figure
from plotly.offline import plot

from .misc import LoadingBar



class Dataset:    
    
    def __init__(self, input_interval, prediction_interval, categories):
        self.input_interval = input_interval
        self.prediction_interval = prediction_interval
        self.categories = categories
    

    def parse_csv(self, filename):
        print('Parsing', filename)
        with open(filename) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')        
            csv_list = np.array(list(csv_reader))
            # delete the first header line
            csv_list = np.delete(csv_list, obj=0, axis=0)
            return csv_list


    def generate_training_set(self, set_size, data):
        
        # shorten variable names
        input_interval = self.input_interval
        prediction_interval = self.prediction_interval
        categories = self.categories
        
        input_set = np.zeros((set_size, input_interval, 4), dtype='float')
        label_set = np.zeros((set_size, len(categories) + 1), dtype='int32') 
        
        csv_list = self.parse_csv(data)
           
        size = len(csv_list)    
        index = 0
        
        lb = LoadingBar(size=set_size, message='Generating training set')
        
        # one iteration of the while loop samples from the price timeline of a 
        # random cryptocurrency and random time interval
        # after checking the date is added to the training set list
        while(index < set_size):
            target_day = np.random.randint(input_interval - 1, 
                                           size - prediction_interval)
            target_crypto = csv_list[target_day][1]
            # if the random time interval is not covering a single crypto
            # then reject it and continue
            if (target_crypto != csv_list[target_day-input_interval + 1][1] or
                target_crypto != csv_list[target_day+prediction_interval][1]):
                continue
            
            start_row = target_day - input_interval + 1
            end_row = start_row + input_interval
            
            target_interval = np.array(csv_list[start_row:end_row, 5:9], 
                                       dtype='float')
            
            # if the standard deviation of the prices in the chosen interval 
            # is zero then reject this example and continue
            if np.std(target_interval) == 0:
                continue             

            # add to training set
            input_set[index] = target_interval
            
            label_set[index] = self.calculate_label(categories, target_day, 
                                                    csv_list, 
                                                    prediction_interval)            
                
            index += 1           
            lb()    
        
        input_set = self.standardize(input_set)
        
        self.training_input_set = input_set
        self.training_label_set = label_set
        
        return input_set, label_set
    
    def calculate_label(self, categories, target_day, csv_list, 
                        prediction_interval):
        
        label = np.zeros((len(categories) + 1), dtype='int32') 
        
        # base_price is the target day close     
        base_price = highest_price = (float)(csv_list[target_day][8]) 
        
        # search highest price in open and close prices of the prediction
        # interval days
        for i in range(prediction_interval):
            highest_price = max(highest_price, 
                                (float)(csv_list[target_day + 1 + i][5]),
                                (float)(csv_list[target_day + 1 + i][8]))

        # Ratio of the highest opening or closing prices of the prediciton 
        # interval days and the target day's close price (>1)
        increment_rate = (float)(highest_price) / (float)(base_price) 
        
        categories.sort(reverse=True)
        set_category = False
        
        # find which category to fit in
        for i, c in enumerate(categories):
            if increment_rate >= 1 + (c / 100):
                label[len(categories) - i] = 1
                set_category = True
                break      
        
        # if no category found, set the base category
        if not set_category:
            label[0] = 1         
            
        return label            
            
    
    def get_training_set(self):
        return self.input_set, self.label_set
        pass
    
    def generate_test_set(self, set_size, data):
        
        input_interval = self.input_interval
        prediction_interval = self.prediction_interval
        categories = self.categories 
        
        input_set = np.zeros((set_size, input_interval, 4), dtype='float')
        label_set = np.zeros((set_size, len(categories) + 1), dtype='int32') 
        
        csv_list = self.parse_csv(test_data)
           
        size = len(csv_list)

        if set_size > size - prediction_interval - input_interval + 1: 
            raise Exception('Maximum test set size is: {}'.format(size - prediction_interval - input_interval - 1))
            
        lb = LoadingBar(size=set_size, message='Generating test set')
        
        for i, target_day in enumerate(range(size-prediction_interval-set_size, size-prediction_interval)):
            target_crypto = csv_list[target_day][1]
            
            start_row = target_day - input_interval + 1
            end_row = start_row + input_interval
            
            target_interval = np.array(csv_list[start_row:end_row, 5:9], 
                                       dtype='float')
            
            # if the standard deviation of the prices in the chosen interval 
            # is zero then reject this example and continue
            if np.std(target_interval) == 0:
                raise Exception('Standard deviation of test set example is 0')             

            # add to training set
            input_set[i] = target_interval
            
            label_set[i] = self.calculate_label(categories, target_day, 
                                                csv_list, prediction_interval) 
                         
            lb()    
        
        self.test_input_set = input_set
        self.test_label_set = label_set
        
        return input_set, label_set
    
    
    def standardize(self, input_set):
        """
        Standardize every training example's input separately by moving the
        mean to 0 and scaling the standard deviation to 1
    
        Parameters
        ----------
        input_set : np.ndarray(3D) - 
            DESCRIPTION.
    
        Returns
        -------
        input_set : TYPE
            DESCRIPTION.
    
        """
        print('Standardize dataset...')
        input_set = deepcopy(input_set)    
        for i in range(input_set.shape[0]):   
            if np.std(input_set[i]) == 0:
                print(input_set[i])
            input_set[i] = (input_set[i] - np.mean(input_set[i])) / np.std(input_set[i])            
        return input_set


    def plot_candlestick(single_input):
    
        open_ = single_input[:,0]
        high_ = single_input[:,1]
        low_ = single_input[:,2]
        close_ = single_input[:,3]
    
        dates = list(range(single_input.shape[0]))
        
        fig = Figure(data=[Candlestick(x=dates,open=open_, high=high_, low=low_, 
                                       close=close_)])
    
        plot(fig)


    def save(self, filename):
        pass