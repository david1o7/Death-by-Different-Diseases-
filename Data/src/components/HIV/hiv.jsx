import React, { useEffect, useState, useMemo } from 'react';
import './hiv.css';
import Navbar from '../Navbar/Navbar.jsx';
const Hiv = () => {
  const [rawData, setRawData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const [selectedCountry, setSelectedCountry] = useState('all');
  const [startYear, setStartYear] = useState('');
  const [endYear, setEndYear] = useState('');
  const [minValue, setMinValue] = useState('');

  const chart_api_base_url = 'http://127.0.0.1:5001/api/charts';

  useEffect(() => {
    fetch('http://127.0.0.1:5000/api/aids/data')
      .then(response => {
        if (!response.ok) {
          throw new Error('Network response was not ok');
        }
        return response.json();
      })
      .then(data => {
        setRawData(data);
        setLoading(false);
      })
      .catch(error => {
        setError(error);
        setLoading(false);
      });
  }, []);

  // Get unique countries and years for filters
  const countries = useMemo(() => {
    const uniqueCountries = [...new Set(rawData.map(item => item.country))];
    return uniqueCountries.sort();
  }, [rawData]);

  const years = useMemo(() => {
    const uniqueYears = [...new Set(rawData.flatMap(item => 
      item.data.map(d => d.year)
    ))];
    return uniqueYears.sort();
  }, [rawData]);

  // Filter data based on selections
  const filteredData = useMemo(() => {
    let filtered = rawData;

    if (selectedCountry && selectedCountry !== 'all') {
      filtered = filtered.filter(item => item.country === selectedCountry);
    }

    if (startYear) {
      filtered = filtered.map(item => ({
        ...item,
        data: item.data.filter(d => d.year >= startYear)
      })).filter(item => item.data.length > 0);
    }

    if (endYear) {
      filtered = filtered.map(item => ({
        ...item,
        data: item.data.filter(d => d.year <= endYear)
      })).filter(item => item.data.length > 0);
    }

    if (minValue) {
      const minVal = parseInt(minValue);
      filtered = filtered.map(item => ({
        ...item,
        data: item.data.filter(d => d.aids_related_deaths_all_ages >= minVal)
      })).filter(item => item.data.length > 0);
    }

    return filtered;
  }, [rawData, selectedCountry, startYear, endYear, minValue]);

  if (loading) {
    return <div className="loading">Loading AIDS data...</div>;
  }

  if (error) {
    return <div className="error">Error: {error.message}</div>;
  }

  return (
    <>
    <Navbar/>
    <div className="hiv-dashboard">
      <h1>AIDS Data Visualization Dashboard</h1>
      
      {/* Filter Controls */}
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="country-select">Country:</label>
          <select 
            id="country-select"
            value={selectedCountry} 
            onChange={(e) => setSelectedCountry(e.target.value)}
          >
            <option value="all">All Countries</option>
            {countries.map(country => (
              <option key={country} value={country}>{country}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="start-year">Start Year:</label>
          <select 
            id="start-year"
            value={startYear} 
            onChange={(e) => setStartYear(e.target.value)}
          >
            <option value="">All Years</option>
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="end-year">End Year:</label>
          <select 
            id="end-year"
            value={endYear} 
            onChange={(e) => setEndYear(e.target.value)}
          >
            <option value="">All Years</option>
            {years.map(year => (
              <option key={year} value={year}>{year}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="min-value">Minimum Value:</label>
          <input
            id="min-value"
            type="number"
            value={minValue}
            onChange={(e) => setMinValue(e.target.value)}
            placeholder="Enter minimum value"
          />
        </div>
      </div>

      {/* AIDS-Related Deaths Section */}
      <section className="chart-section">
        <h2>AIDS-Related Deaths</h2>
        <div className="charts-grid">
          <div className="chart-container">
            <h3>Global AIDS-Related Deaths: 1990-2021</h3>
            <img src={`${chart_api_base_url}/deaths_global`} alt="Global AIDS-Related Deaths" />
          </div>
          <div className="chart-container">
            <h3>AIDS-Related Deaths by Age Group: Adults vs Children</h3>
            <img src={`${chart_api_base_url}/deaths_by_group`} alt="Deaths by Age Group" />
          </div>
          <div className="chart-container">
            <h3>Top 10 Countries with Highest AIDS-Related Deaths</h3>
            <img src={`${chart_api_base_url}/top_deaths`} alt="Top Countries Deaths" />
          </div>
        </div>
      </section>

      {/* HIV Prevalence Section */}
      <section className="chart-section">
        <h2>HIV Prevalence</h2>
        <div className="charts-grid">
          <div className="chart-container">
            <h3>Global HIV Prevalence Rate Among Adults (15-49 years)</h3>
            <img src={`${chart_api_base_url}/prevalence_global`} alt="Global HIV Prevalence" />
          </div>
          <div className="chart-container">
            <h3>HIV Prevalence Among Young People (15-24 years)</h3>
            <img src={`${chart_api_base_url}/prevalence_young`} alt="Young People Prevalence" />
          </div>
        </div>
      </section>

      {/* New HIV Infections Section */}
      <section className="chart-section">
        <h2>New HIV Infections</h2>
        <div className="charts-grid">
          <div className="chart-container">
            <h3>Global New HIV Infections: Annual Incidence</h3>
            <img src={`${chart_api_base_url}/infections_global`} alt="Global New Infections" />
          </div>
          <div className="chart-container">
            <h3>New HIV Infections by Age Group: Adults vs Children</h3>
            <img src={`${chart_api_base_url}/infections_by_group`} alt="Infections by Age Group" />
          </div>
          <div className="chart-container">
            <h3>Top 10 Countries with Highest New HIV Infections</h3>
            <img src={`${chart_api_base_url}/top_infections`} alt="Top Countries Infections" />
          </div>
        </div>
      </section>

      {/* People Living with HIV Section */}
      <section className="chart-section">
        <h2>People Living with HIV (PLHIV)</h2>
        <div className="charts-grid">
          <div className="chart-container">
            <h3>Global People Living with HIV (PLHIV): Total Population</h3>
            <img src={`${chart_api_base_url}/plhiv_global`} alt="Global PLHIV" />
          </div>
          <div className="chart-container">
            <h3>People Living with HIV by Age Group: Adults vs Children</h3>
            <img src={`${chart_api_base_url}/plhiv_by_group`} alt="PLHIV by Age Group" />
          </div>
          <div className="chart-container">
            <h3>Top 10 Countries with Highest HIV Population</h3>
            <img src={`${chart_api_base_url}/top_plhiv`} alt="Top Countries PLHIV" />
          </div>
        </div>
      </section>

      {/* Filtered Data Table */}
      <section className="data-section">
        <h2>Filtered Data</h2>
        {filteredData.length === 0 ? (
          <p>No data matches your current filters.</p>
        ) : (
          <div className="data-tables">
            {filteredData.map(country => (
              <div key={country.country} className="country-data">
                <h3>{country.country}</h3>
                <table>
                  <thead>
                    <tr>
                      <th>Year</th>
                      <th>AIDS Deaths (All Ages)</th>
                      <th>New Infections (All Ages)</th>
                      <th>People Living with HIV</th>
                      <th>HIV Prevalence (Adults %)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {country.data.map((item, index) => (
                      <tr key={index}>
                        <td>{item.year}</td>
                        <td>{item.aids_related_deaths_all_ages?.toLocaleString() || 'N/A'}</td>
                        <td>{item.new_hiv_infections_all_ages?.toLocaleString() || 'N/A'}</td>
                        <td>{item.people_living_with_hiv_total?.toLocaleString() || 'N/A'}</td>
                        <td>{item.hiv_prevalence_adults || 'N/A'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
    </>
  );
};

export default Hiv;
