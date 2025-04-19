# ECCC Thunderstorm Outlook API

This repository provides an automated API for Environment and Climate Change Canada (ECCC) Thunderstorm Outlook data. The data is automatically updated every 6 hours and made available as a JSON file through GitHub.

## Features

- Automatically fetches thunderstorm outlooks from all ECCC Storm Prediction Centers:
  - OSPC (Ontario Storm Prediction Centre)
  - QSPC (Quebec Storm Prediction Centre)
  - PSPC (Prairie Storm Prediction Centre - MB, SK, AB)
  - ASPC (Atlantic Storm Prediction Centre - NB, NS, PE, NL)
  - BCSPC (British Columbia Storm Prediction Centre)
- Updates every 6 hours via GitHub Actions
- Provides data for 12-hour, 24-hour, and 36-hour forecasts
- Maintains version history of forecasts
- Easy-to-use JSON format

## Data Source

The data is sourced directly from ECCC's official data distribution website:
`https://dd.alpha.weather.gc.ca/thunderstorm-outlooks/`

## How to Use

### Direct JSON Access

Access the latest thunderstorm outlook data directly through the raw GitHub URL:

```
https://raw.githubusercontent.com/WxHaydenC/ECCCThunderstormGeojsonAPI/main/outlooks_data.json
```

### Python Example

```python
import requests
import json

def fetch_outlook_data():
    url = "https://raw.githubusercontent.com/WxHaydenC/ECCCThunderstormGeojsonAPI/main/outlooks_data.json"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

# Usage example
data = fetch_outlook_data()
if data:
    # Access day 1 (12-hour) forecasts
    day1_forecasts = data["day1"]
    
    # Access day 2 (24-hour) forecasts
    day2_forecasts = data["day2"]
    
    # Access day 3 (36-hour) forecasts
    day3_forecasts = data["day3"]
    
    # Get last update time
    last_updated = data["last_updated"]
```

## Data Structure

```json
{
  "day1": {
    "YYYYMMDD": {
      // GeoJSON data for 12-hour forecast
    }
  },
  "day2": {
    "YYYYMMDD": {
      // GeoJSON data for 24-hour forecast
    }
  },
  "day3": {
    "YYYYMMDD": {
      // GeoJSON data for 36-hour forecast
    }
  },
  "last_updated": "ISO-8601 timestamp",
  "metadata": {
    "source": "Environment and Climate Change Canada",
    "description": "Thunderstorm Outlook Data",
    "update_frequency": "Every 6 hours",
    "regions": {
      // Information about Storm Prediction Centers
    }
  }
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This project is not affiliated with Environment and Climate Change Canada. The data provided by this API belongs to ECCC.
