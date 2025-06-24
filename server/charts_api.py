import pandas as pd
import matplotlib.pyplot as plt
import io
from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import matplotlib.ticker as mtick # Import for percentage formatting

app = Flask(__name__)
CORS(app)

# Set matplotlib backend to 'Agg' for non-interactive plotting
plt.switch_backend('Agg')

# Function to load and preprocess data
def load_data():
    """
    Loads, cleans, and prepares the AIDS dataset from 'aids.csv'.
    Converts relevant columns to numeric and fills NaN values with 0.
    """
    try:
        df = pd.read_csv('aids.csv')
        df.columns = df.columns.str.strip()

        # Identify and convert columns starting with 'Data.' to numeric
        numeric_cols = [col for col in df.columns if col.startswith('Data.')]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any remaining NaN values in these columns with 0
        df.fillna(0, inplace=True)
        return df
    except Exception as e:
        print(f"Error loading or processing data: {e}")
        return None

# Helper function to save plot to BytesIO
def save_plot_to_bytesio(fig):
    """
    Saves a matplotlib figure to a BytesIO object as a PNG image.
    Closes the figure after saving to free up memory.
    """
    img = io.BytesIO()
    fig.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plt.close(fig) # Close the figure to free memory
    return img

# --- Existing Endpoints (Improved) ---

@app.route('/api/charts/deaths_global')
def deaths_global():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6)) # Use subplots for better control
    deaths = df.groupby('Year')['Data.AIDS-Related Deaths.All Ages'].sum()
    
    ax.plot(deaths.index, deaths.values, color='#E74C3C', linewidth=2, marker='o', markersize=4)
    ax.set_title('Global AIDS-Related Deaths (All Ages): 1990-2021', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y') # Prevent scientific notation on y-axis
    fig.autofmt_xdate() # Auto-format x-axis labels for dates

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/deaths_by_group')
def deaths_by_group():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    adults = df.groupby('Year')['Data.AIDS-Related Deaths.Adults'].sum()
    children = df.groupby('Year')['Data.AIDS-Related Deaths.Children'].sum()
    
    ax.plot(adults.index, adults.values, label='Adults (15+)', color='#C0392B', linewidth=2)
    ax.plot(children.index, children.values, label='Children (0-14)', color='#2980B9', linewidth=2)
    
    ax.set_title('AIDS-Related Deaths by Age Group: Adults vs Children (Global)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/prevalence_global')
def prevalence_global():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    prevalence = df.groupby('Year')['Data.HIV Prevalence.Adults'].mean() # Mean prevalence across countries
    
    ax.plot(prevalence.index, prevalence.values, color='#8E44AD', linewidth=2, marker='o', markersize=4)
    ax.set_title('Global Average HIV Prevalence Rate Among Adults (15-49 years)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Prevalence Rate (%)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) # Format as percentage
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/prevalence_young')
def prevalence_young():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    men = df.groupby('Year')['Data.HIV Prevalence.Young Men'].mean()
    women = df.groupby('Year')['Data.HIV Prevalence.Young Women'].mean()
    
    ax.plot(men.index, men.values, label='Young Men (15-24)', color='#3498DB', linewidth=2)
    ax.plot(women.index, women.values, label='Young Women (15-24)', color='#E91E63', linewidth=2)
    
    ax.set_title('HIV Prevalence Among Young People (15-24 years) (Global Average)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Prevalence Rate (%)', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) # Format as percentage
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/infections_global')
def infections_global():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    infections = df.groupby('Year')['Data.New HIV Infections.All Ages'].sum()
    
    ax.plot(infections.index, infections.values, color='#F39C12', linewidth=2, marker='o', markersize=4)
    ax.set_title('Global New HIV Infections: Annual Incidence (All Ages)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of New Infections', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/infections_by_group')
def infections_by_group():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    adults = df.groupby('Year')['Data.New HIV Infections.Adults'].sum()
    children = df.groupby('Year')['Data.New HIV Infections.Children'].sum()
    
    ax.plot(adults.index, adults.values, label='Adults (15+)', color='#D35400', linewidth=2)
    ax.plot(children.index, children.values, label='Children (0-14)', color='#2ECC71', linewidth=2)
    
    ax.set_title('New HIV Infections by Age Group: Adults vs Children (Global)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of New Infections', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/plhiv_global')
def plhiv_global():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    plhiv = df.groupby('Year')['Data.People Living with HIV.Total'].sum()
    
    ax.plot(plhiv.index, plhiv.values, color='#27AE60', linewidth=2, marker='o', markersize=4)
    ax.set_title('Global People Living with HIV (PLHIV): Total Population', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of People', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/plhiv_by_group')
def plhiv_by_group():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    adults = df.groupby('Year')['Data.People Living with HIV.Adults'].sum()
    children = df.groupby('Year')['Data.People Living with HIV.Children'].sum()
    
    ax.plot(adults.index, adults.values, label='Adults (15+)', color='#2ECC71', linewidth=2)
    ax.plot(children.index, children.values, label='Children (0-14)', color='#1ABC9C', linewidth=2)
    
    ax.set_title('People Living with HIV by Age Group: Adults vs Children (Global)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of People', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/top_deaths')
def top_deaths():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year]
    top_10 = df_latest.nlargest(10, 'Data.AIDS-Related Deaths.All Ages').sort_values(
        'Data.AIDS-Related Deaths.All Ages', ascending=True
    )
    
    fig, ax = plt.subplots(figsize=(10, 7)) # Adjusted size for readability
    ax.barh(top_10['Country'], top_10['Data.AIDS-Related Deaths.All Ages'], color='#E74C3C')
    ax.set_xlabel('Number of AIDS-Related Deaths', fontsize=12)
    ax.set_title(f'Top 10 Countries with Highest AIDS-Related Deaths ({latest_year})', fontsize=14, fontweight='bold')
    # No need to invert_yaxis() after sorting ascending=True for barh
    ax.ticklabel_format(style='plain', axis='x') # Prevent scientific notation on x-axis
    fig.tight_layout()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/top_infections')
def top_infections():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year]
    top_10 = df_latest.nlargest(10, 'Data.New HIV Infections.All Ages').sort_values(
        'Data.New HIV Infections.All Ages', ascending=True
    )
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top_10['Country'], top_10['Data.New HIV Infections.All Ages'], color='#F39C12')
    ax.set_xlabel('Number of New HIV Infections', fontsize=12)
    ax.set_title(f'Top 10 Countries with Highest New HIV Infections ({latest_year})', fontsize=14, fontweight='bold')
    ax.ticklabel_format(style='plain', axis='x')
    fig.tight_layout()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/top_plhiv')
def top_plhiv():
    df = load_data()
    if df is None:
        return "Data not found", 404
        
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year]
    top_10 = df_latest.nlargest(10, 'Data.People Living with HIV.Total').sort_values(
        'Data.People Living with HIV.Total', ascending=True
    )
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top_10['Country'], top_10['Data.People Living with HIV.Total'], color='#27AE60')
    ax.set_xlabel('Number of People Living with HIV', fontsize=12)
    ax.set_title(f'Top 10 Countries with Highest HIV Population ({latest_year})', fontsize=14, fontweight='bold')
    ax.ticklabel_format(style='plain', axis='x')
    fig.tight_layout()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

# --- New Endpoints ---

@app.route('/api/charts/aids_orphans')
def aids_orphans():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    orphans = df.groupby('Year')['Data.AIDS-Related Deaths.AIDS Orphans'].sum()
    
    ax.plot(orphans.index, orphans.values, color='#9B59B6', linewidth=2, marker='o', markersize=4)
    ax.set_title('Global AIDS-Related Orphans Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Orphans', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/deaths_by_gender')
def deaths_by_gender():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    female_deaths = df.groupby('Year')['Data.AIDS-Related Deaths.Female Adults'].sum()
    male_deaths = df.groupby('Year')['Data.AIDS-Related Deaths.Male Adults'].sum()
    
    ax.plot(female_deaths.index, female_deaths.values, label='Female Adults', color='#FF69B4', linewidth=2)
    ax.plot(male_deaths.index, male_deaths.values, label='Male Adults', color='#4682B4', linewidth=2)
    
    ax.set_title('AIDS-Related Deaths by Gender (Adults, Global)', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Deaths', fontsize=12)
    ax.legend(fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.ticklabel_format(style='plain', axis='y')
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/incidence_rate')
def incidence_rate():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    fig, ax = plt.subplots(figsize=(10, 6))
    incidence = df.groupby('Year')['Data.New HIV Infections.Incidence Rate Among Adults'].mean()
    
    ax.plot(incidence.index, incidence.values, color='#A0522D', linewidth=2, marker='o', markersize=4)
    ax.set_title('Global Average HIV Incidence Rate Among Adults', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Incidence Rate (per 100 people)', fontsize=12)
    ax.grid(True, linestyle='--', alpha=0.6)
    # Potentially format as percentage if the rate is 0-1
    # ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) 
    fig.autofmt_xdate()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

@app.route('/api/charts/country_profile/<country_name>')
def country_profile(country_name):
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    country_data = df[df['Country'].str.lower() == country_name.lower()]
    
    if country_data.empty:
        return jsonify({"error": f"Data for country '{country_name}' not found."}), 404

    fig, ax1 = plt.subplots(figsize=(12, 8))

    # Plotting Deaths
    ax1.plot(country_data['Year'], country_data['Data.AIDS-Related Deaths.All Ages'], 
             color='#E74C3C', label='AIDS-Related Deaths', marker='o', markersize=4)
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Number of Deaths / New Infections', color='#E74C3C', fontsize=12)
    ax1.tick_params(axis='y', labelcolor='#E74C3C')
    ax1.ticklabel_format(style='plain', axis='y')

    # Create a second y-axis for New Infections
    ax2 = ax1.twinx()
    ax2.plot(country_data['Year'], country_data['Data.New HIV Infections.All Ages'], 
             color='#F39C12', label='New HIV Infections', marker='x', markersize=4, linestyle='--')
    ax2.tick_params(axis='y', labelcolor='#F39C12')
    ax2.ticklabel_format(style='plain', axis='y')

    # Create a third y-axis for PLHIV
    ax3 = ax1.twinx()
    # Move the right spine of ax3 to the right of the second y-axis
    ax3.spines['right'].set_position(('outward', 60)) 
    ax3.plot(country_data['Year'], country_data['Data.People Living with HIV.Total'], 
             color='#27AE60', label='People Living with HIV', marker='s', markersize=4, linestyle=':')
    ax3.tick_params(axis='y', labelcolor='#27AE60')
    ax3.ticklabel_format(style='plain', axis='y')

    fig.suptitle(f'Key AIDS Indicators for {country_name} Over Time', fontsize=16, fontweight='bold')
    ax1.grid(True, linestyle='--', alpha=0.6)
    fig.autofmt_xdate()

    # Combine legends from all axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    lines3, labels3 = ax3.get_legend_handles_labels()
    ax3.legend(lines + lines2 + lines3, labels + labels2 + labels3, loc='upper left', bbox_to_anchor=(0.0, 1.15))

    fig.tight_layout(rect=[0, 0, 0.85, 1]) # Adjust layout to make space for the third y-axis label

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')


@app.route('/api/charts/top_prevalence')
def top_prevalence():
    df = load_data()
    if df is None:
        return "Data not found", 404
    
    latest_year = df['Year'].max()
    df_latest = df[df['Year'] == latest_year]
    # Use mean for prevalence as it's a rate
    top_10 = df_latest.nlargest(10, 'Data.HIV Prevalence.Adults').sort_values(
        'Data.HIV Prevalence.Adults', ascending=True
    )
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.barh(top_10['Country'], top_10['Data.HIV Prevalence.Adults'], color='#8E44AD')
    ax.set_xlabel('HIV Prevalence Rate (%)', fontsize=12)
    ax.set_title(f'Top 10 Countries with Highest Adult HIV Prevalence ({latest_year})', fontsize=14, fontweight='bold')
    ax.xaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0)) # Format as percentage
    fig.tight_layout()

    return send_file(save_plot_to_bytesio(fig), mimetype='image/png')

if __name__ == '__main__':
    # Using a different port to avoid conflict with other services
    app.run(debug=True, port=5001) 

