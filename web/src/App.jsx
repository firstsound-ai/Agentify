import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from '@douyinfe/semi-ui';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Home from './pages/Home';
import Questionnaire from './pages/Questionnaire';
import './App.css';
import RequirementForm from './pages/RequirementForm';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  
  return (
    <div className="app-wrapper">
      <Header darkMode={darkMode} setDarkMode={setDarkMode} />
      <Sidebar />
      <Layout className="home-layout">
        <div className="main-content-area">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/questionnaire" element={<Questionnaire />} />
            <Route path="/requirement-form" element={<RequirementForm />} />
          </Routes>
        </div>
      </Layout>
    </div>
  );
}

export default App;