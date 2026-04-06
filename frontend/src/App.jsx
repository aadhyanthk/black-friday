import {useState, useEffect} from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  const [item, setItem] = useState({item_name: 'Loading...', stock_count: 100});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const itemId = 1;
  const backendUrl = 'http://127.0.0.1:8000';

  // Function to fetch current stock
  const fetchStock = async () => {
    try {
      const response = await axios.get(`${backendUrl}/inventory/${itemId}`);
      setItem(response.data);
    } catch (error) {
      console.error('Failed to fetch stock:', error);
    }
  };

  // Poll the backend every 2 seconds to simulate a live "Flash Sale"
  useEffect(() => {
    fetchStock();
    const interval = setInterval(() => fetchStock(), 2000);
    return () => clearInterval(interval);
  }, []);

  const handlePurchase = async () => {
    setLoading(true);
    setMessage('');
    try {
      await axios.post(`${backendUrl}/checkout`, {
        item_id: itemId,
        user_identifier: (Math.random() * 10000).toString()
      });
      setMessage('Success! Item Secured.');
      fetchStock();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Purchase Failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <div className="sale-badge">BLACK FRIDAY LIVE</div>
      <h1>{item.item_name}</h1>
      
      <div className="stock-card">
        <p>Units Remaining</p>
        <div className={`stock-number ${item.stock_count < 20 ? 'critical' : ''}`}>
          {item.stock_count}
        </div>
      </div>

      <button 
        className="buy-btn" 
        onClick={() => handlePurchase()} 
        disabled={loading || item.stock_count <= 0}
      >
        {loading ? 'PROCESSING...' : item.stock_count <= 0 ? 'SOLD OUT' : 'GET IT NOW'}
      </button>

      {message && <p className="status-msg">{message}</p>}
    </div>
  );
};

export default App;