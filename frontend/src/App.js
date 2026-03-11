import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [solutions, setSolutions] = useState([]);
  const [category, setCategory] = useState('');
  const [country, setCountry] = useState('');
  const [csvPreview, setCsvPreview] = useState([]);
  const [working, setWorking] = useState(false);

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

  const previewCombinedCSV = async () => {
    try {
      const res = await fetch('/data/solutions_combined.csv');
      const text = await res.text();
      const rows = text.split('\n').filter(Boolean).map(r => r.split(','));
      setCsvPreview(rows.slice(0, 20));
    } catch (e) {
      console.error(e);
      setCsvPreview([]);
    }
  };

  const triggerFetchSolutions = async (opts = {}) => {
    setWorking(true);
    try {
      await fetch('/api/admin/fetch_solutions/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(opts),
      });
      // started; you can poll or later refresh preview
    } catch (e) {
      console.error(e);
    }
    setWorking(false);
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
          <button onClick={() => triggerFetchSolutions({ run_scraper: true })} disabled={working}>Run Scraper</button>
          <button onClick={() => triggerFetchSolutions({ upload_to_sheet: true, sheet_id: '' })} disabled={working}>Upload Combined to Sheet</button>
          <button onClick={previewCombinedCSV}>Preview Combined CSV</button>
        </div>
        <ul>
          {solutions.map(s => (
            <li key={s.id}>
              <strong>{s.name}</strong> — {s.category} — {s.location?.country}
            </li>
          ))}
        </ul>

        {csvPreview.length > 0 && (
          <div style={{ textAlign: 'left', marginTop: 16 }}>
            <h3>Combined CSV preview (first {csvPreview.length} rows)</h3>
            <table>
              <tbody>
                {csvPreview.map((row, idx) => (
                  <tr key={idx}>{row.map((c, i) => <td key={i} style={{padding:4, border:'1px solid #ccc'}}>{c}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
