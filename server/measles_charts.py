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

# Set the Matplotlib backend to 'Agg' which is suitable for
# generating images without a GUI frontend, crucial for server environments.
plt.switch_backend('Agg')

def load_measles_data():
    """
    Loads the measles data from 'data.csv', cleans it, and prepares it for analysis.

    The function assumes the data has headers on the second row (index 1)
    and that the first column is 'Countries, territories and areas'.
    It renames this column to 'country' and converts all year columns
    to numeric, filling any non-numeric values (like empty strings) with 0.
    """
    try:
        # Read the CSV file, using the second row as the header.
        df = pd.read_csv('data.csv', header=1)
        # Rename the country column for easier access.
        df.rename(columns={"Countries, territories and areas": "country"}, inplace=True)

        # Identify columns that represent years. These are all columns
        # except the 'country' column.
        year_columns = [col for col in df.columns if col != 'country']

        # Convert year columns to numeric, coercing errors will turn
        # non-numeric values into NaN (Not a Number).
        for col in year_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any NaN values (introduced by 'coerce' or originally present) with 0.
        # This assumes missing case data means 0 cases.
        df.fillna(0, inplace=True)

        return df
    except FileNotFoundError:
        print("Error: data.csv not found. Please ensure the file is in the correct directory.")
        return pd.DataFrame() # Return an empty DataFrame on error
    except Exception as e:
        print(f"An error occurred while loading or cleaning data: {e}")
        return pd.DataFrame()

def save_plot_to_bytesio(fig):
    """
    Saves a Matplotlib figure to an in-memory BytesIO object as a PNG image.
    This avoids saving files to disk and allows direct streaming.

    Args:
        fig (matplotlib.figure.Figure): The Matplotlib figure to save.

    Returns:
        io.BytesIO: An in-memory binary stream containing the PNG image data.
    """
    img = io.BytesIO()
    # Save the figure to the BytesIO object as PNG.
    # bbox_inches='tight' removes extra whitespace around the plot.
    # dpi sets the resolution of the image.
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    # Seek to the beginning of the stream so it can be read by send_file.
    img.seek(0)
    # Close the figure to free up memory, crucial when generating many plots.
    plt.close(fig)
    return img

@app.route('/api/measles/charts/global_cases')
def global_cases():
    """
    API endpoint to generate a line chart showing global measles cases over time.
    """
    df = load_measles_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500

    # Exclude the 'country' column to sum cases across years.
    years = [col for col in df.columns if col != 'country']
    # Ensure years are sorted for proper plotting.
    years.sort() 
    
    # Calculate total cases per year by summing across countries.
    totals = df[years].sum()

    # Create the plot.
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, totals.values, color='#E67E22', marker='o')
    ax.set_title('Global Measles Cases Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Cases', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate() # Automatically format x-axis labels for dates.
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/measles/charts/top_countries')
def top_countries():
    """
    API endpoint to generate a horizontal bar chart showing the top 10 countries
    by total measles cases across all available years.
    """
    df = load_measles_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500

    years = [col for col in df.columns if col != 'country']
    # Calculate total cases for each country.
    df['total_cases'] = df[years].sum(axis=1)
    # Get the top 10 countries.
    top = df.nlargest(10, 'total_cases')

    # Create the plot.
    fig, ax = plt.subplots(figsize=(10, 6))
    # barh creates horizontal bars.
    ax.barh(top['country'], top['total_cases'], color='#3498DB')
    ax.set_title('Top 10 Countries by Total Measles Cases (All Years)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Total Cases', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    plt.gca().invert_yaxis() # Invert y-axis to have the highest bar at the top.
    plt.tight_layout() # Adjust plot to ensure everything fits.
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/measles/charts/country_profile')
def country_profile():
    """
    API endpoint to generate a line chart showing measles cases for a specific
    country over time. The country name is passed as a query parameter.
    """
    country = request.args.get('country')
    if not country:
        return jsonify({'error': 'Country parameter is required'}), 400

    df = load_measles_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500

    # Filter the DataFrame for the specified country.
    row = df[df['country'].str.contains(country, case=False, na=False)]
    
    if row.empty:
        return jsonify({'error': f'Country "{country}" not found'}), 404
    
    # If multiple matches, take the first one (or refine search).
    # For now, let's take the exact match if available, otherwise the first fuzzy match.
    exact_match_row = df[df['country'] == country]
    if not exact_match_row.empty:
        row = exact_match_row
    else:
        # If no exact match, and fuzzy match found multiple, maybe pick first.
        # For this example, we assume `row` will contain the best match or be empty.
        pass


    years = [col for col in df.columns if col not in ['country', 'total_cases']] # Exclude total_cases if it was added
    years.sort() # Ensure years are sorted for plotting

    # Get cases for the selected country across all years.
    cases = row[years].values.flatten()

    # Create the plot.
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(years, cases, color='#2ECC71', marker='o')
    ax.set_title(f'Measles Cases in {row["country"].iloc[0]} Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Cases', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate()
    
    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/measles/charts/compare_countries')
def compare_countries():
    """
    API endpoint to generate a line chart comparing measles cases over time
    for multiple user-specified countries.
    Countries are passed as a comma-separated string in the 'countries' query parameter.
    """
    countries_param = request.args.get('countries')
    if not countries_param:
        return jsonify({'error': 'At least one country name is required in the "countries" parameter (comma-separated).'}), 400

    # Split the comma-separated string into a list of country names.
    country_names = [c.strip() for c in countries_param.split(',') if c.strip()]
    if not country_names:
        return jsonify({'error': 'No valid country names provided.'}), 400

    df = load_measles_data()
    if df.empty:
        return jsonify({'error': 'Data could not be loaded or is empty'}), 500

    # Filter data for the requested countries.
    # Using isin() for efficient filtering of multiple countries.
    selected_df = df[df['country'].isin(country_names)]

    if selected_df.empty:
        return jsonify({'error': f'None of the specified countries ({", ".join(country_names)}) were found.'}), 404
    
    # Identify year columns, excluding 'country' and 'total_cases' (if present).
    years = [col for col in df.columns if col not in ['country', 'total_cases']]
    years.sort() # Ensure years are in chronological order

    # Create the plot.
    fig, ax = plt.subplots(figsize=(12, 7)) # Slightly larger for multiple lines
    
    colors = ['#E74C3C', '#27AE60', '#F39C12', '#8E44AD', '#3498DB', '#1ABC9C', '#D35400', '#C0392B', '#2C3E50', '#7F8C8D']
    color_index = 0

    # Plot each selected country's cases over time.
    for index, row in selected_df.iterrows():
        country_name = row['country']
        cases = row[years].values.flatten()
        ax.plot(years, cases, label=country_name, marker='.', color=colors[color_index % len(colors)])
        color_index += 1

    ax.set_title(f'Measles Cases Over Time for Selected Countries', fontsize=16, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Cases', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1)) # Place legend outside to avoid overlap
    fig.autofmt_xdate()
    plt.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for the legend.

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

if __name__ == "__main__":
    # When running locally, the app will be accessible at http://127.0.0.1:8082
    # debug=True allows for automatic reloading on code changes and provides a debugger.
    app.run(debug=True, port=8082)

