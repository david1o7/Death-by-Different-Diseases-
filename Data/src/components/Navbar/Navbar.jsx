import React, { useState } from 'react'
import './Navbar.css'
import { Link } from 'react-router-dom'

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav className='navbar-container'>
      <div className='navbar-logo'>
        Deaths by Various Diseases
      </div>
      <button className='navbar-hamburger' onClick={() => setMenuOpen(m => !m)} aria-label="Toggle menu">
        <span className='bar'></span>
        <span className='bar'></span>
        <span className='bar'></span>
      </button>
      <ul className={`navbar-links${menuOpen ? ' open' : ''}`}>
        <li><Link to="/hiv" onClick={() => setMenuOpen(false)}>HIV</Link></li>
        <li><Link to="/measles" onClick={() => setMenuOpen(false)}>Measles</Link></li>
        <li><Link to="/malaria" onClick={() => setMenuOpen(false)}>Malaria</Link></li>
      </ul>
    </nav>
  )
}

export default Navbar
