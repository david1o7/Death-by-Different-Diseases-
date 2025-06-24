import React from 'react';
import './Hero.css';

const Hero = () => {
  return (
    <section className="hero-section">
      <div className="hero-content">
        <h1 className="hero-title">Global Disease Dashboard</h1>
        <p className="hero-description">
          Explore interactive visualizations and data insights on deaths and infections from HIV, Measles, Malaria, and more. Empower your research and awareness with up-to-date statistics.
        </p>
        <a href="#dashboard" className="hero-cta">Get Started</a>
      </div>
    </section>
  );
};

export default Hero;
