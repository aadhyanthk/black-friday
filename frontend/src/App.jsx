import {useState, useEffect} from 'react';
import axios from 'axios';
import './App.css';

const App = () => {
  // Initialize as null so we can detect when the API has actually responded
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const itemId = 1;
  const backendUrl = 'http://127.0.0.1:8000';

  const fetchStock = async () => {
    try {
      const response = await axios.get(`${backendUrl}/inventory/${itemId}`);
      setItem(response.data);
    } catch (error) {
      console.error('API Fetch Error:', error);
    }
  };

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
        user_identifier: `user_${Math.floor(Math.random() * 10000)}`
      });
      setMessage('SUCCESS: Item secured in your cart!');
      fetchStock();
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Transaction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Visual Guard: Show a loading state until the first database response arrives
  if (!item) {
    return (
      <div className="container">
        <div className="loading-spinner">Initializing Flash Sale Data...</div>
      </div>
    );
  }

  return (
    <div className="container">
      <div className="sale-badge">BLACK FRIDAY LIVE</div>
      
      <header className="product-header">
        <h1>{item.item_name}</h1>
        <p className="description">High-performance processing for the next generation of computing.</p>
      </header>

      <div className="stock-card">
        <p className="label">REMAINING STOCK</p>
        <div className={`stock-number ${item.stock_count < 20 ? 'critical' : ''}`}>
          {item.stock_count}
        </div>
        {item.stock_count < 20 && item.stock_count > 0 && (
          <p className="urgency-note">Hurry! Almost gone.</p>
        )}
      </div>

      <div className="action-area">
        <button 
          className="buy-btn" 
          onClick={() => handlePurchase()} 
          disabled={loading || item.stock_count <= 0}
        >
          {loading ? 'RESERVING UNIT...' : item.stock_count <= 0 ? 'SOLD OUT' : 'CLAIM OFFER NOW'}
        </button>

        {message && (
          <div className={`status-msg ${message.includes('SUCCESS') ? 'success' : 'error'}`}>
            {message}
          </div>
        )}
      </div>

      <footer className="security-footer">
        <p>🔒 Secure Transaction | Pessimistic Row-Level Locking Active</p>
      </footer>
    </div>
  );
};

export default App;