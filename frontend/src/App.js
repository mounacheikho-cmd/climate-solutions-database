import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [solutions, setSolutions] = useState([]);
  const [category, setCategory] = useState('');
  const [country, setCountry] = useState('');

  useEffect(() => {
    fetchSolutions();
  }, []);

  const fetchSolutions = async () => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (country) params.append('country', country);
    const res = await fetch(`/api/solutions/?${params.toString()}`);
    const data = await res.json();
    setSolutions(data.results || []);
  };

  const exportCSV = () => {
    const params = new URLSearchParams();
    if (category) params.append('category', category);
    if (country) params.append('country', country);
    window.location.href = `/api/solutions/export_csv/?${params.toString()}`;
  };

  return (
    <div className="App">
      <header className="App-header">
        <h2>Climate Solutions</h2>
        <div style={{ marginBottom: 12 }}>
          <input placeholder="category" value={category} onChange={e => setCategory(e.target.value)} />
          <input placeholder="country" value={country} onChange={e => setCountry(e.target.value)} />
          <button onClick={fetchSolutions}>Filter</button>
          <button onClick={exportCSV}>Export CSV</button>
        </div>
        <ul>
          {solutions.map(s => (
            <li key={s.id}>
              <strong>{s.name}</strong> — {s.category} — {s.location?.country}
            </li>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
