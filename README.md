# data-tracker
A simple service that tracks data

## The code

### language

- The program requires python 3 interpreter

### required packages

- flask
- pandas
- threading

## Querying the data from the code's API

### since the API is on the air, let's assume its address is 'http://127.0.0.1:5000/', you can reach the data with these GET queries:

1. http://127.0.0.1:5000/get_metrics
   - Returning a list of possible metrics
2. http://127.0.0.1:5000/get_price/PUT_YOUR_METRIC_HERE
   - Returning a list of dicts (every dict has the key 'update_time' and the other keys are markets with their prices)
3. http://127.0.0.1:5000/get_rank/PUT_YOUR_METRIC_HERE
   - Returning a dict with all the markets as keys and their Standard Deviations as values 
4. http://127.0.0.1:5000/get_data
   - Returning a dict with all the metrics as keys and prices (with get_price's pattern) as values

### Also, you can clean the data with this POST query:

- http://127.0.0.1:5000/restart_data
