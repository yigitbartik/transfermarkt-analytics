# 🚀 Quick Start Guide - Transfermarkt Analytics Pro

## 5-Minute Setup

### Step 1: Extract Files
```bash
unzip transfermarkt-analytics-pro.zip
cd transfermarkt-analytics
```

### Step 2: Run the App (Choose your OS)

#### Windows
```bash
run.bat
```

#### macOS/Linux
```bash
chmod +x run.sh
./run.sh
```

### Step 3: Open Browser
The app will open automatically at:
```
http://localhost:8501
```

## What You Can Do

### Dashboard
- 📊 See all leagues, clubs, players, and matches at a glance
- 💰 View total market values by league
- 📋 Browse supported leagues with club counts

### Clubs
- 🏆 Browse clubs in any league
- 📊 Sort by market value or name
- 💵 See market values and player counts
- 📈 View top 15 clubs visualization
- 📍 Market value vs players scatter plot

### Players
- 👥 View all players in a club
- 🔍 Filter by position (GK, DEF, MID, FWD)
- 📊 Sort by market value, age, or name
- 📈 See position distribution and age statistics
- 💰 Average market value calculations

### Matches
- 🎯 See all match results in a league
- 📅 Sorted by date (newest first)
- 📊 Status indicators (Finished, Scheduled)
- 🏟️ Stadium information

### Match Analysis (Advanced)
- 📈 Multi-source statistics comparison
- 📊 Side-by-side possession, shots, passes
- 📉 Interactive comparison charts
- 🔗 Data from SofaScore and FotMob

### Statistics
- 💰 League market value distribution (pie chart)
- 👥 Average player market value by league
- 📊 Comparative analysis

### Settings
- 📡 Data source status monitoring
- 🔄 Update/refresh data
- 🗑️ Database management options

## First Time Setup

### 1. Initial Data Load (15-20 minutes)
Click **"🔄 Update Data"** button in the sidebar:
- Scrapes Transfermarkt for all leagues and clubs
- Downloads player rosters for each club
- Fetches match results
- Links matches with external sources

### 2. View Your Data
Once complete, explore all sections to see the data!

### 3. Regular Updates
Click the update button whenever you want fresh data.

## Common Tasks

### Find a Specific Club
1. Go to **"⚽ Clubs"**
2. Select league from dropdown
3. Table shows all clubs in that league
4. Click column header to sort

### View Team Roster
1. Go to **"👤 Players"**
2. Select club from dropdown
3. Optionally filter by position
4. See all player details

### Compare Two Clubs' Market Values
1. Go to **"⚽ Clubs"**
2. Select league
3. Chart shows top 15 clubs
4. Sort table by market value

### Analyze a Specific Match
1. Go to **"📊 Match Analysis"**
2. Select league and match from dropdowns
3. View statistics from SofaScore/FotMob if available
4. See interactive comparison charts

### Track Data Source Status
1. Go to **"⚙️ Settings"**
2. Check data source status table
3. See last sync times and any errors

## Troubleshooting

### Problem: App won't start
**Solution**: Make sure Python 3.9+ is installed
```bash
python --version  # Should show 3.9 or higher
```

### Problem: "No module named streamlit"
**Solution**: Dependencies not installed
```bash
pip install -r requirements.txt
```

### Problem: "Database is locked"
**Solution**: Close all instances and restart
```bash
# Or delete and recreate database
rm transfermarkt.db
```

### Problem: Data takes forever to load
**Normal on first run!** First sync takes 15-20 minutes as it scrapes all data.
Subsequent updates are much faster.

### Problem: Some matches have no external stats
**Normal!** Not all matches can be automatically linked to external sources.
Still shows Transfermarkt data.

### Problem: Port 8501 already in use
**Solution**: Use different port
```bash
streamlit run app.py --server.port 8502
```

## System Requirements

- **CPU**: Any modern processor (Intel, AMD, Apple Silicon)
- **RAM**: 512MB minimum (1GB recommended)
- **Disk**: 500MB free space
- **OS**: Windows 10+, macOS 10.15+, Linux (any)
- **Python**: 3.9, 3.10, 3.11, or 3.12

## File Structure

```
transfermarkt-analytics/
├── app.py                 ← Main application
├── config.py              ← Settings
├── run_scraper.py         ← Data collection
├── database/
│   ├── db.py             ← Database setup
│   └── models.py         ← Data structure
├── scraper/
│   ├── clubs.py          ← Transfermarkt clubs
│   ├── players.py        ← Transfermarkt players
│   ├── matches.py        ← Transfermarkt matches
│   ├── sofascore.py      ← SofaScore API
│   └── fotmob.py         ← FotMob API
├── run.bat               ← Windows startup
├── run.sh                ← Mac/Linux startup
├── transfermarkt.db      ← Database (created after first run)
└── .streamlit/
    └── config.toml       ← Streamlit settings
```

## Advanced: Docker Deployment

### Using Docker Compose (Recommended)
```bash
docker-compose up
```
App runs at `http://localhost:8501`

### Using Docker Directly
```bash
docker build -t transfermarkt-analytics .
docker run -p 8501:8501 transfermarkt-analytics
```

## Advanced: Custom Configuration

Edit `config.py` to customize:
```python
# Enable/disable data sources
ENABLE_SOFASCORE = True
ENABLE_FOTMOB = True

# Database location
DATABASE_URL = "sqlite:///./transfermarkt.db"

# Request settings
REQUEST_TIMEOUT = 10
```

## Tips & Tricks

1. **Faster Loading**: Use filters to view subset of data
2. **Better Charts**: Interact with charts (hover, zoom, pan)
3. **Export Data**: Right-click charts to save as PNG
4. **Table Export**: Copy table data to clipboard
5. **Refresh**: Press R key in browser to refresh app

## Data Sources

### Transfermarkt
- Clubs, players, market values
- Basic match information
- No API, web scraping

### SofaScore
- Detailed match statistics
- Player ratings and performance
- Free API access

### FotMob
- Extended match analytics
- Possession and shot data
- Free API access

## Performance Tips

1. First data load takes time - be patient!
2. Close browser tabs you don't need
3. Use filters to reduce visible data
4. Database queries are cached
5. Restart app if it slows down

## Next Steps

1. ✅ **Install and run** the app
2. ✅ **Click "Update Data"** to populate database
3. ✅ **Explore the pages** to get familiar with data
4. ✅ **Read detailed README.md** for more info
5. ✅ **Check CHANGELOG.md** for what's new

## Support & Help

For detailed documentation: See **README.md**
For version history: See **CHANGELOG.md**
For troubleshooting: See **README.md - Troubleshooting**

## Quick Links

- 📖 [Full Documentation](README.md)
- 📝 [Change Log](CHANGELOG.md)
- 🐛 [Report Issues](https://github.com)
- 💡 [Request Features](https://github.com)

---

**Happy Analyzing! ⚽📊**

**Version**: 2.0.0  
**Last Updated**: 2024-03-31
