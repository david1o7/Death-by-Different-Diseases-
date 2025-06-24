import React from 'react'
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom'
import Hiv from './components/HIV/hiv'
import NotFound from './components/NotFound.jsx'
import Measles from './components/Measles/Measles.jsx'
import HomePage from './components/HomePage/HomePage.jsx'
import Malaria from './components/Malaria/Malaria.jsx'
const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path='/hiv' element={<Hiv/>}></Route>
        <Route path="/measles" element={<Measles />} />
        <Route path='/malaria' element={<Malaria />}></Route>
        <Route path='*' element={<NotFound />} />
        
      </Routes>
    </Router>
  )
}

export default App
