import pandas as pd
import matplotlib.pyplot as plt
import io
from flask import Flask, send_file, request, jsonify
from flask_cors import CORS

# Initialize the Flask application
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing (CORS) for all routes,
# allowing web pages from different origins to access the API.
CORS(app)

# Set the Matplotlib backend to 'Agg'. This is important for server-side
# rendering of plots, as it does not require a graphical user interface.
plt.switch_backend('Agg')

def load_malaria_data():
    """
    Loads malaria data from 'malaria_data.csv', renames the country column,
    and performs robust data cleaning to ensure all year columns are numeric.
    This step is crucial for generating accurate data visualizations.
    """
    try:
        # Read the CSV file, assuming the second row contains the actual headers.
        df = pd.read_csv('malaria_data.csv', header=1)
        
        # Rename the 'Countries, territories and areas' column to 'country' for easier access.
        # This provides the primary "relatable category" for geographical analysis.
        df.rename(columns={"Countries, territories and areas": "country"}, inplace=True)
        
        # Identify columns that represent years (all columns except 'country').
        year_columns = [col for col in df.columns if col != 'country']
        
        # Data Cleaning for Accuracy:
        # Iterate through each year column to clean and convert data to integers.
        # This is a critical step to ensure that the data used for plotting is
        # purely numerical, preventing errors and ensuring graph accuracy.
        # 1. .astype(str): Ensures all entries are treated as strings to handle mixed types.
        # 2. .str.replace(',', ''): Removes commas (e.g., in "1,234" to "1234") which would prevent numeric conversion.
        # 3. .str.extract(r'(\d+)'): Extracts only the digits from the string. This is
        #    a powerful step to handle non-numeric characters (like asterisks indicating estimates),
        #    text (like "No data"), or ranges, by robustly taking only the first sequence of digits.
        #    This ensures only valid numerical data points are considered.
        # 4. .fillna(0): Replaces any values that couldn't be converted to digits (e.g., empty strings,
        #    or entries that were entirely non-numeric after extraction) with 0. This makes sure
        #    missing data points are consistently treated as zero deaths for numerical operations.
        # 5. .astype(int): Converts the cleaned numeric strings to integers for precise calculations.
        for col in year_columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.extract(r'(\d+)').fillna(0).astype(int)
        
        return df
    except FileNotFoundError:
        print("Error: malaria_data.csv not found. Please ensure the file is in the correct directory.")
        return pd.DataFrame() # Return an empty DataFrame on error
    except Exception as e:
        print(f"An unexpected error occurred during data loading or cleaning: {e}")
        return pd.DataFrame()

def save_plot_to_bytesio(fig):
    """
    Saves a Matplotlib figure to an in-memory BytesIO object as a PNG image.
    This method allows the Flask app to directly serve images without saving
    them to the file system, improving efficiency and security.
    """
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0) # Rewind the buffer to the beginning.
    plt.close(fig) # Close the figure to free up memory.
    return img

def _get_sorted_year_columns(df):
    """
    Helper function to identify and sort year columns from the DataFrame.
    """
    # Exclude 'country' and 'total_deaths' (if it exists) from year columns.
    years = [col for col in df.columns if col not in ['country', 'total_deaths']]
    # Sort years numerically to ensure chronological plotting for accurate trends.
    return sorted(years, key=lambda y: int(y.strip()))

@app.route('/api/malaria/charts/global_deaths')
def global_deaths():
    """
    API endpoint to generate a line chart showing global malaria deaths over time.
    This provides a high-level "relatable category" for understanding the overall
    impact of malaria globally across all available years. The sum ensures
    an accurate representation of global trends.
    """
    df = load_malaria_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500
    
    years_sorted = _get_sorted_year_columns(df)
    
    # Calculate total deaths per year by summing across all countries.
    totals = df[years_sorted].sum()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years_sorted, totals.values, color='#16a085', marker='o') # Teal color for plot
    ax.set_title('Global Malaria Deaths Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate() # Auto-format x-axis labels for better readability.
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/malaria/charts/top_countries')
def top_countries():
    """
    API endpoint to generate a horizontal bar chart showing the top 10 countries
    by total malaria deaths across all available years.
    This categorizes countries by their total burden, providing "relatable categories"
    of the most affected nations, with an accurate sum of deaths over time.
    """
    df = load_malaria_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500
    
    years = _get_sorted_year_columns(df)
    # Calculate total deaths for each country across all years.
    # This sum is accurate because non-numeric values were handled in load_malaria_data.
    df['total_deaths'] = df[years].sum(axis=1)
    
    # Get the top 10 countries with the highest total deaths.
    top = df.nlargest(10, 'total_deaths')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top['country'], top['total_deaths'], color='#2980b9') # Blue color for bars
    ax.set_title('Top 10 Countries by Total Malaria Deaths (All Years)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Total Deaths', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    plt.gca().invert_yaxis() # Invert y-axis to display the highest bar at the top for better readability.
    plt.tight_layout() # Adjust layout to prevent labels from overlapping.
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/malaria/charts/country_profile')
def country_profile():
    """
    API endpoint to generate a line chart showing malaria deaths for a specific
    country over time. The country name is passed as a query parameter.
    This allows for granular analysis of a single "relatable category" (a specific country)
    with accurate time-series data.
    """
    country_name_param = request.args.get('country')
    if not country_name_param:
        return jsonify({'error': 'Country parameter is required'}), 400
    
    df = load_malaria_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500
    
    # Search for the country, allowing for partial or case-insensitive matches.
    # Using .str.lower() for consistent case-insensitive comparison.
    row = df[df['country'].str.lower() == country_name_param.lower()]
    
    # If no exact match, try a contains search as a fallback for flexibility.
    if row.empty:
        row = df[df['country'].str.contains(country_name_param, case=False, na=False)]
    
    if row.empty:
        return jsonify({'error': f'Country "{country_name_param}" not found'}), 404
    
    # If multiple matches, take the first one or the most relevant if refinement is needed.
    # For now, if there's more than one, we'll use the first found (e.g., "Congo" vs. "Democratic Republic of the Congo")
    # For a real application, you might want to return a list of matches and let the user choose.
    selected_country_row = row.iloc[0]
    
    years_sorted = _get_sorted_year_columns(df)
    
    # Extract death data for the selected country. This is accurate due to prior data cleaning.
    deaths = selected_country_row[years_sorted].values.flatten()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years_sorted, deaths, color='#e67e22', marker='o') # Orange color for plot
    ax.set_title(f'Malaria Deaths in {selected_country_row["country"]} Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate()
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/malaria/charts/compare_countries')
def compare_countries():
    """
    API endpoint to generate a line chart comparing malaria deaths over time
    for multiple user-specified countries.
    Countries are passed as a comma-separated string in the 'countries' query parameter.
    This provides a direct comparison between custom "relatable categories" (user-chosen countries)
    with accurate time-series trends for each.
    """
    countries_param = request.args.get('countries')
    if not countries_param:
        return jsonify({'error': 'At least one country name is required in the "countries" parameter (comma-separated).'}), 400
    
    # Split the comma-separated string into a list of country names, stripping whitespace.
    country_names = [c.strip().lower() for c in countries_param.split(',') if c.strip()]
    if not country_names:
        return jsonify({'error': 'No valid country names provided.'}), 400
    
    df = load_malaria_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500
    
    # Filter the DataFrame to include only the requested countries (case-insensitive comparison).
    selected_df = df[df['country'].str.lower().isin(country_names)]
    
    if selected_df.empty:
        # Check which countries were not found for a more informative error message.
        found_countries = selected_df['country'].str.lower().tolist()
        not_found = [c for c in country_names if c not in found_countries]
        return jsonify({'error': f'None of the specified countries ({", ".join(not_found)}) were found or have data.'}), 404
    
    years_sorted = _get_sorted_year_columns(df)
    
    fig, ax = plt.subplots(figsize=(12, 7)) # Larger figure for multiple lines
    
    # Define a palette of distinct colors for different countries.
    colors = ['#E74C3C', '#27AE60', '#F39C12', '#8E44AD', '#3498DB', '#1ABC9C', '#D35400', '#C0392B', '#2C3E50', '#7F8C8D']
    color_index = 0
    
    # Plot malaria deaths for each selected country.
    for index, row in selected_df.iterrows():
        country_display_name = row['country'] # Use original case for display
        deaths = row[years_sorted].values.flatten()
        # Use a different color for each country, cycling through the palette.
        ax.plot(years_sorted, deaths, label=country_display_name, marker='.', color=colors[color_index % len(colors)])
        color_index += 1
    
    ax.set_title(f'Malaria Deaths Over Time for Selected Countries', fontsize=16, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    # Place legend outside the plot area to prevent overlap with lines.
    # Adjusted bbox_to_anchor for better spacing with many lines.
    ax.legend(loc='upper left', bbox_to_anchor=(1.02, 1), borderaxespad=0.) 
    fig.autofmt_xdate() # Auto-format x-axis labels.
    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make sufficient space for the legend.
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

if __name__ == "__main__":
    # When running locally, the app will be accessible at http://127.0.0.1:8083
    # debug=True allows for automatic reloading on code changes and provides a debugger.
    app.run(debug=True, port=8083)

