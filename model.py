import numpy as np
import pandas as pd

class PVForecaster:
    def __init__(self):
        self.model = None #TODO: add a model here
        
        self.data = None
        self.data_15min = None

    def load_data(self, history_data):
        # Convert the input data to a pandas DataFrame
        df = pd.DataFrame(history_data[0])
        # Select columns
        df = df[['last_updated', 'state']]

        # Convert the 'last_updated' column to datetime format
        df['last_updated'] = pd.to_datetime(df['last_updated'])

        # Convert the 'state' column to numeric values
        df['state'] = pd.to_numeric(df['state'])

        # Set the 'last_updated' column as the index of the DataFrame
        df.set_index('last_updated', inplace=True)

        df.sort_index(inplace=True)

        self.data = df

    def preprocess_data(self):
        # Transform data to 15min intervals summing the values
        self.data_15min = self.data.resample('15T').sum()

    def train(self):
        pass

    def predict(self):
        return 7.27

    def evaluate(self, X_test, y_test):
        pass