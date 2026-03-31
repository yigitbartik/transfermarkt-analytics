# ⚽ Transfermarkt Analytics Pro

A professional football analytics platform that aggregates data from multiple sources including Transfermarkt, SofaScore, and FotMob. Provides detailed match statistics, player analysis, and league insights.

## 🚀 Features

### Data Sources
- **Transfermarkt**: Clubs, players, market values, basic match data
- **SofaScore**: Detailed match statistics, player performances
- **FotMob**: Extended match analytics and statistics
- **Multi-source integration**: Automatically link and combine data from different sources

### Analytics & Insights
- 📊 **Dashboard**: Overview of all leagues, clubs, and players
- ⚽ **Club Analysis**: Market values, squad composition, player distribution
- 👥 **Player Profiles**: Detailed player information, market values, positions, age
- 🏟️ **Match Results**: Complete match data, scores, dates
- 📈 **Advanced Statistics**: Multi-source match statistics comparison
- 💰 **Market Value Analysis**: League-wide and club-level market value insights

### Data Management
- 🔄 **Automatic Updates**: Schedule or manual data refresh
- 📡 **Multi-Source Sync**: Track which data comes from which source
- 🗄️ **SQLite Database**: Efficient local storage with SQLAlchemy ORM
- 🔍 **Advanced Filtering**: Filter by league, club, position, market value, etc.

## 📋 Requirements

- Python 3.9+
- pip (Python package manager)
- 500MB free disk space (for database and data)

## 🔧 Installation

### Option 1: Using pip (Recommended)

```bash
# Clone or extract the project
cd transfermarkt-analytics

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Option 2: Direct installation

```bash
# Extract the ZIP file
cd transfermarkt-analytics

# Install dependencies
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Run the Streamlit App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 2. Update Data

Click the "🔄 Update Data" button in the sidebar to fetch the latest information from all sources.

This may take 10-15 minutes on first run as it:
- Scrapes all leagues and clubs from Transfermarkt
- Scrapes all players for each club
- Fetches match data
- Attempts to link matches with external sources (SofaScore, FotMob)

### 3. Explore Analytics

Navigate through different sections:
- **Dashboard**: Overview and key metrics
- **Clubs**: Browse clubs by league with detailed statistics
- **Players**: View player lists with filtering and sorting
- **Matches**: See match results and scores
- **Match Analysis**: View detailed statistics from multiple sources
- **Statistics**: League-wide insights and comparisons
- **Settings**: Manage data and sources

## 📁 Project Structure

```
transfermarkt-analytics/
├── app.py                    # Main Streamlit application
├── config.py                 # Configuration settings
├── run_scraper.py           # Data collection orchestration
├── database/
│   ├── __init__.py
│   ├── db.py               # Database connection
│   └── models.py           # SQLAlchemy ORM models
├── scraper/
│   ├── __init__.py
│   ├── clubs.py            # Transfermarkt clubs scraper
│   ├── players.py          # Transfermarkt players scraper
│   ├── matches.py          # Transfermarkt matches scraper
│   ├── sofascore.py        # SofaScore API integration
│   └── fotmob.py           # FotMob API integration
├── requirements.txt         # Python dependencies
├── setup.py                # Package setup
└── README.md               # This file
```

## 🗄️ Database Schema

### Core Tables

- **leagues**: Football leagues (Premier League, La Liga, etc.)
- **clubs**: Football clubs with market values and details
- **players**: Player information including positions and market values
- **matches**: Match results and basic information
- **match_statistics**: Detailed statistics from multiple sources
- **player_performances**: Individual player performance in matches
- **data_sources**: Tracking of data source status and sync times

## ⚙️ Configuration

Edit `config.py` to customize:

```python
# Enable/disable data sources
ENABLE_SOFASCORE = True
ENABLE_FOTMOB = True
ENABLE_MATCH_LINKING = True

# Database URL
DATABASE_URL = "sqlite:///./transfermarkt.db"

# Request settings
REQUEST_TIMEOUT = 10
RETRY_ATTEMPTS = 3
```

## 🔄 Data Update Process

### Transfermarkt Scraping
1. Iterates through all configured leagues
2. Fetches all clubs for each league
3. Fetches all players for each club
4. Fetches match data
5. Parses market values and other information
6. Stores in database with error handling

### External Source Integration
1. Searches for matches on SofaScore using team names
2. Retrieves detailed match statistics
3. Links matches across sources
4. Stores statistics with source attribution

## 📊 Data Sources Details

### Transfermarkt
- **Type**: Web scraping (BeautifulSoup)
- **Data**: Clubs, players, market values, match results
- **Update Frequency**: Manual or scheduled
- **Rate Limiting**: Polite delays between requests

### SofaScore
- **Type**: REST API
- **Data**: Match statistics, player performances, ratings
- **Endpoints**: Teams search, match details, player stats
- **Data Quality**: Very detailed and accurate

### FotMob
- **Type**: REST API  
- **Data**: Match analytics, possession, shots, passes
- **Endpoints**: Match search, league matches
- **Data Quality**: Good coverage with analytical insights

## 🐛 Troubleshooting

### Issue: "Database is locked"
**Solution**: Close all instances of the app and delete `transfermarkt.db` if needed.

### Issue: "No data showing"
**Solution**: Click "Update Data" button to fetch initial data from sources.

### Issue: Scraper running slow
**Solution**: This is normal on first run. Subsequent updates are faster as it only adds new data.

### Issue: API rate limiting errors
**Solution**: Wait a few minutes before retrying. Requests are already rate-limited internally.

### Issue: Some matches missing external statistics
**Solution**: Not all matches can be linked to external sources due to name variations or data differences.

## 🔐 Privacy & Terms

- **Transfermarkt**: Data is scraped following their robots.txt rules
- **SofaScore**: Uses public API (check their terms of service)
- **FotMob**: Data accessed through official endpoints
- **Legal**: Use for personal/educational purposes only. Commercial use may require permissions.

## 📈 Performance Tips

1. **Initial Setup**: First data sync takes 10-15 minutes
2. **Incremental Updates**: Subsequent updates are much faster
3. **Database**: Stored locally, no internet required after initial sync
4. **Filtering**: Use filters to reduce data and improve performance
5. **Memory**: If running slowly, close other applications

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional data sources (Understat, InStat, etc.)
- Prediction models for match outcomes
- Player comparison tools
- Transfer market analysis
- Performance optimizations

## 📝 License

This project is provided as-is for educational and personal use.

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the code comments
3. Check data source status in Settings page
4. Ensure all dependencies are installed correctly

## 🔮 Future Enhancements

- [ ] Player transfer predictions
- [ ] Match outcome predictions
- [ ] Advanced player comparison tools
- [ ] Performance trend analysis
- [ ] Custom report generation
- [ ] Data export functionality
- [ ] Team formation analysis
- [ ] Injury tracker
- [ ] Fixture difficulty ratings
- [ ] Player rating predictions

## 📚 References

- [Transfermarkt](https://www.transfermarkt.com/)
- [SofaScore](https://www.sofascore.com/)
- [FotMob](https://www.fotmob.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

**Made with ⚽ and Python**  
Last Updated: 2024
