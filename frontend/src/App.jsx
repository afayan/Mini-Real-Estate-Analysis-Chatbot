import React, { useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [chartData, setChartData] = useState([]);
  const [tableData, setTableData] = useState([]);
  const [areas, setAreas] = useState([]);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSummary("");
    setChartData([]);
    setTableData([]);

    if (!query.trim()) return;

    try {
      setLoading(true);
      const res = await axios.post("http://127.0.0.1:8000/api/analyze/", {
        query,
      });
      setSummary(res.data.summary);
      setChartData(res.data.chartData || []);
      setTableData(res.data.tableData || []);
      setAreas(res.data.areas || []);
    } catch (err) {
      setError("Server error. Check if Django is running.");
    } finally {
      setLoading(false);
    }
  };

  const groupedByArea = areas.reduce((acc, area) => {
    acc[area] = chartData.filter((row) => row.area === area);
    return acc;
  }, {});

  return (
    <div className="container py-4">
      <h2 className="mb-3 text-center">Mini Real Estate Analysis Chatbot</h2>

      <form onSubmit={handleSubmit} className="mb-4 d-flex gap-2">
        <input
          className="form-control"
          placeholder="Type a query like 'Analyze Wakad'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button className="btn btn-primary" type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Send"}
        </button>
      </form>

      {error && <div className="alert alert-danger">{error}</div>}

      {summary && (
        <div className="card mb-4">
          <div className="card-header">Summary</div>
          <div className="card-body">
            <p>{summary}</p>
          </div>
        </div>
      )}

      {areas.length > 0 && (
        <div className="mb-4">
          <h5>Trends</h5>
          {areas.map((area) => (
            <div className="card mb-3" key={area}>
              <div className="card-header">{area}</div>
              <div className="card-body" style={{ height: 250 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={groupedByArea[area]}>
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="avg_price" name="Avg Price" />
                    <Line
                      type="monotone"
                      dataKey="avg_demand"
                      name="Avg Demand"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ))}
        </div>
      )}

      {tableData.length > 0 && (
        <div className="card">
          <div className="card-header">Filtered Data</div>
          <div className="card-body table-responsive">
            <table className="table table-sm table-striped">
              <thead>
                <tr>
                  {Object.keys(tableData[0]).map((key) => (
                    <th key={key}>{key.toUpperCase()}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tableData.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((val, i) => (
                      <td key={i}>{val}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
