# Bitcoin Logarithmic Spiral Visualization API

A FastAPI application that generates interactive logarithmic spiral charts of Bitcoin price data.

## Prerequisites

Before starting, ensure you have the following installed:

- **Python 3.8+**
- **MySQL Server 8.0+**
- **pip** (Python package manager)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/kOaDT/bitcoin-spiral-api.git
cd bitcoin-spiral-api
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### 4.1 Create BitcoinPrice Table

```sql
CREATE TABLE BitcoinPrice (
    id INT AUTO_INCREMENT PRIMARY KEY,
    price DECIMAL(20, 8) NOT NULL,
    dateAdd DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_dateAdd (dateAdd),
    INDEX idx_price (price)
);
```

#### 4.2 Import Sample Data

Insert some sample Bitcoin price data:

```sql
INSERT INTO BitcoinPrice (price, dateAdd) VALUES
(50000.00, '2024-01-01 00:00:00'),
(52000.00, '2024-01-02 00:00:00'),
(48000.00, '2024-01-03 00:00:00'),
(51000.00, '2024-01-04 00:00:00'),
(53000.00, '2024-01-05 00:00:00'),
(49000.00, '2024-01-06 00:00:00'),
(54000.00, '2024-01-07 00:00:00');
```

### 5. Environment Configuration

Create a `.env` file in the project root:

```bash
touch .env
```

Add the following configuration:

```env
# Database Configuration
DB_USER=bitcoin_user
DB_PASS=SecurePassword123!
DB_HOST=localhost
DB_PORT=3306
DB_NAME=bitcoin_data

# Application Configuration
DEBUG=False
```

### 6. Run the Application

#### Development Mode

```bash
# Using the start script (recommended)
chmod +x start.sh
./start.sh
```

Or manually:

```bash
python -m app.main
```

#### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The application will be available at: **http://localhost:8000**

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main dashboard with logarithmic spiral chart |
| `/health` | GET | Health check endpoint |

### Query Parameters

- `days` (optional): Limit data to last N days (e.g., `/?days=365`)

## Database Schema

### BitcoinPrice Table

| Column | Type | Description |
|--------|------|-------------|
| `id` | INT | Primary key, auto-increment |
| `price` | DECIMAL(20,8) | Bitcoin price in USD |
| `dateAdd` | DATETIME | Timestamp of price record |

## Data Import

### Real-time Data Integration

To continuously update Bitcoin prices, you can:

1. **Use a cron job** to fetch data from cryptocurrency APIs
2. **Connect to WebSocket streams** for real-time updates
3. **Import CSV files** with historical data

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request