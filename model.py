import numpy as np
import pandas as pd
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics


class PVForecaster:
    def __init__(self):
        self.model = Prophet()  # Initialize the Prophet model
        
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
        self.data_15min = self.data.resample('15T').sum().reset_index()
        # Rename columns to match Prophet's expectations
        self.data_15min.columns = ['ds', 'y']
        print(self.data_15min)
        # Ensure the DataFrame is in the correct format for Prophet
        self.data = self.data.reset_index()
        # Remove timezone information from the 'ds' column
        self.data['last_updated'] = self.data['last_updated'].dt.tz_localize(None)
        self.data.columns = ['ds', 'y']

    def train(self):
        # Fit the model with the original data
        self.model.fit(self.data)

    def predict(self, periods=1, freq='15T'):
        # Create future DataFrame for predictions. Adjust the frequency as needed.
        future = self.model.make_future_dataframe(periods=periods, freq=freq)
        # Generate forecast
        forecast = self.model.predict(future)

        # Get next 15 min prediction
        next_15min = forecast.iloc[-1]['yhat']

        return next_15min

    def evaluate(self):
        ''' Evaluate Prophet Model '''
        # Perform cross-validation
        df_cv = cross_validation(self.model, initial='7 days', period='2 days', horizon='15 minutes')
        # Calculate performance metrics
        df_p = performance_metrics(df_cv)

        mape = df_p['mape'].mean() if 'mape' in df_p.columns else np.nan
        smape = df_p['smape'].mean() if 'smape' in df_p.columns else np.nan
        rmse = df_p['rmse'].mean() if 'rmse' in df_p.columns else np.nan
        mdape = df_p['mdape'].mean() if 'mdape' in df_p.columns else np.nan

        # Return the performance metrics
        return f"MAPE: {mape:.2f} | SMAPE: {smape:.2f} | RMSE: {rmse:.2f} | MDAPE: {mdape:.2f}"
        
        
