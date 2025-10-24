import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_data(num_records=1000):
    np.random.seed(42)

    # Vehicles data
    vehicle_types = ['Truck A', 'Truck B', 'Truck C']
    vehicles = pd.DataFrame({
        'vehicle_id': [f'V{i:03d}' for i in range(10)],
        'vehicle_type': np.random.choice(vehicle_types, 10),
        'age_years': np.random.randint(1, 10, 10),
        'last_maintenance': [datetime.now() - timedelta(days=np.random.randint(30, 365)) for _ in range(10)]
    })

    # Routes data
    route_terrains = ['Flat', 'Hilly', 'Mountainous']
    routes = pd.DataFrame({
        'route_id': [f'R{i:03d}' for i in range(5)],
        'distance_km': np.random.randint(100, 1000, 5),
        'terrain': np.random.choice(route_terrains, 5)
    })

    # Fuel prices (simulated historical data)
    dates = [datetime.now() - timedelta(days=i) for i in range(365)]
    fuel_prices = pd.DataFrame({
        'date': dates,
        'price_per_liter_mxn': np.random.uniform(20, 25, 365) + np.sin(np.arange(365)/30) * 2
    })
    fuel_prices['date'] = fuel_prices['date'].dt.date # Only keep date for merging

    # Generate trip data
    data = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(num_records):
        trip_date = start_date + timedelta(days=np.random.randint(0, 365))
        vehicle = vehicles.sample(1).iloc[0]
        route = routes.sample(1).iloc[0]
        
        # Base consumption (km/liter)
        base_consumption_kpl = np.random.uniform(2.5, 4.5) 
        
        # Adjust consumption based on vehicle type, age, terrain
        if vehicle['vehicle_type'] == 'Truck B':
            base_consumption_kpl *= 0.95 # Truck B is more efficient
        elif vehicle['vehicle_type'] == 'Truck C':
            base_consumption_kpl *= 0.85 # Truck C is less efficient

        base_consumption_kpl *= (1 - vehicle['age_years'] * 0.02) # Older vehicles less efficient

        if route['terrain'] == 'Hilly':
            base_consumption_kpl *= 0.9
        elif route['terrain'] == 'Mountainous':
            base_consumption_kpl *= 0.8

        # Simulate load impact (randomly)
        load_factor = np.random.uniform(0.8, 1.2) # 0.8 for light load, 1.2 for heavy load
        consumption_kpl = base_consumption_kpl * load_factor

        # Simulate some anomalies (e.g., sudden drop in efficiency)
        if np.random.rand() < 0.02: # 2% chance of anomaly
            consumption_kpl *= np.random.uniform(0.5, 0.7) # Significantly worse efficiency

        distance = route['distance_km'] * np.random.uniform(0.8, 1.2) # Actual distance might vary
        fuel_consumed_liters = distance / consumption_kpl
        
        # Get fuel price for the trip date
        current_fuel_price = fuel_prices[fuel_prices['date'] == trip_date.date()]['price_per_liter_mxn'].values
        if len(current_fuel_price) == 0:
            current_fuel_price = fuel_prices['price_per_liter_mxn'].mean() # Fallback
        else:
            current_fuel_price = current_fuel_price[0]

        fuel_cost = fuel_consumed_liters * current_fuel_price
        
        data.append({
            'trip_id': i,
            'date': trip_date,
            'vehicle_id': vehicle['vehicle_id'],
            'vehicle_type': vehicle['vehicle_type'],
            'vehicle_age_years': vehicle['age_years'],
            'last_maintenance': vehicle['last_maintenance'],
            'route_id': route['route_id'],
            'route_distance_km': route['distance_km'],
            'terrain': route['terrain'],
            'actual_distance_km': distance,
            'fuel_consumed_liters': fuel_consumed_liters,
            'fuel_cost_mxn': fuel_cost,
            'kpl': consumption_kpl, # Kilometers per liter
            'load_factor': load_factor
        })

    df = pd.DataFrame(data)
    return df, vehicles, routes, fuel_prices

if __name__ == '__main__':
    df_trips, df_vehicles, df_routes, df_fuel_prices = generate_data(num_records=5000)
    
    # Save to CSV for easy loading in Streamlit
    df_trips.to_csv(r'C:\Users\Advan\Downloads\PR\Marco\fuel_dashboard\trips_data.csv', index=False)
    df_vehicles.to_csv(r'C:\Users\Advan\Downloads\PR\Marco\fuel_dashboard\vehicles_data.csv', index=False)
    df_routes.to_csv(r'C:\Users\Advan\Downloads\PR\Marco\fuel_dashboard\routes_data.csv', index=False)
    df_fuel_prices.to_csv(r'C:\Users\Advan\Downloads\PR\Marco\fuel_dashboard\fuel_prices_data.csv', index=False)
    print("Synthetic data generated and saved to CSV files.")
