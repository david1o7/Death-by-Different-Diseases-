import React, { useEffect, useState, useMemo } from 'react';
import './Malaria.css';
import Navbar from '../Navbar/Navbar.jsx';

const chart_api_base_url = 'http://127.0.0.1:8083/api/malaria/charts';
const data_api_url = 'http://127.0.0.1:5000/api/malaria/data';

const Malaria = () => {
  const [rawData, setRawData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [selectedCountry, setSelectedCountry] = useState('all');
  const [startYear, setStartYear] = useState('');
  const [endYear, setEndYear] = useState('');
  const [minCases, setMinCases] = useState('');

  useEffect(() => {
    setLoading(true);
    fetch(data_api_url)
      .then(response => {
        if (!response.ok) throw new Error('Network response was not ok');
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
    const uniqueYears = [...new Set(rawData.flatMap(item => item.data.map(d => d.year)))];
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
    if (minCases) {
      const minVal = parseInt(minCases);
      filtered = filtered.map(item => ({
        ...item,
        data: item.data.filter(d => parseInt(d.cases) >= minVal)
      })).filter(item => item.data.length > 0);
    }
    return filtered;
  }, [rawData, selectedCountry, startYear, endYear, minCases]);

  // For compare countries chart
  const [compareCountries, setCompareCountries] = useState([]);
  const [compareUrl, setCompareUrl] = useState('');
  useEffect(() => {
    if (compareCountries.length > 0) {
      setCompareUrl(`${chart_api_base_url}/compare_countries?countries=${compareCountries.join(',')}`);
    } else {
      setCompareUrl('');
    }
  }, [compareCountries]);

  if (loading) {
    return <div className="loading">Loading Malaria data...</div>;
  }
  if (error) {
    return <div className="error">Error: {error.message}</div>;
  }

  return (
    <>
      <Navbar />
      <div className="malaria-dashboard">
        <h1>Malaria Data Visualization Dashboard</h1>

        {/* Filter Controls */}
        <div className="filters">
          <div className="filter-group">
            <label htmlFor="country-select">Country:</label>
            <select
              id="country-select"
              value={selectedCountry}
              onChange={e => setSelectedCountry(e.target.value)}
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
              onChange={e => setStartYear(e.target.value)}
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
              onChange={e => setEndYear(e.target.value)}
            >
              <option value="">All Years</option>
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
          <div className="filter-group">
            <label htmlFor="min-cases">Minimum Deaths:</label>
            <input
              id="min-cases"
              type="number"
              value={minCases}
              onChange={e => setMinCases(e.target.value)}
              placeholder="Enter minimum deaths"
            />
          </div>
        </div>

        {/* Malaria Charts Section */}
        <section className="chart-section">
          <h2>Malaria Charts</h2>
          <div className="charts-grid">
            <div className="chart-container">
              <h3>Global Malaria Deaths Over Time</h3>
              <img src={`${chart_api_base_url}/global_deaths`} alt="Global Malaria Deaths" />
            </div>
            <div className="chart-container">
              <h3>Top 10 Countries by Total Malaria Deaths</h3>
              <img src={`${chart_api_base_url}/top_countries`} alt="Top Countries Malaria Deaths" />
            </div>
            <div className="chart-container">
              <h3>Country Profile</h3>
              <img
                src={selectedCountry !== 'all' ? `${chart_api_base_url}/country_profile?country=${encodeURIComponent(selectedCountry)}` : ''}
                alt="Country Malaria Profile"
                style={{ display: selectedCountry !== 'all' ? 'block' : 'none' }}
              />
              {selectedCountry === 'all' && <div style={{textAlign:'#16a085',color:'#16a085'}}>Select a country to view its profile chart.</div>}
            </div>
            <div className="chart-container">
              <h3>Compare Multiple Countries</h3>
              <select
                multiple
                value={compareCountries}
                onChange={e => {
                  const options = Array.from(e.target.selectedOptions, option => option.value);
                  setCompareCountries(options);
                }}
                style={{ minHeight: '100px' }}
              >
                {countries.map(country => (
                  <option key={country} value={country}>{country}</option>
                ))}
              </select>
              {compareCountries.length > 0 ? (
                <img src={compareUrl} alt="Compare Countries Malaria" style={{marginTop: '10px'}} />
              ) : (
                <div style={{textAlign:'#16a085',color:'#16a085',marginTop:'10px'}}>Select countries to compare.</div>
              )}
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
                        <th>Malaria Deaths</th>
                      </tr>
                    </thead>
                    <tbody>
                      {country.data.map((item, idx) => (
                        <tr key={idx}>
                          <td>{item.year}</td>
                          <td>{item.cases?.toLocaleString() || 'N/A'}</td>
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

export default Malaria;
