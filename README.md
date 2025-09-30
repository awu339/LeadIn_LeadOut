# Prime Day Analysis Dashboard

A comprehensive Streamlit application for analyzing Amazon transaction and campaign data with support for lead-in/lead-out analysis and key performance metrics calculation.

## Features

- **Multi-file Data Processing**: Upload and process transaction data and campaign data (SP, SB, SD)
- **Data Cleaning**: Automatic filtering of Non-Amazon sales channels and date normalization
- **Comprehensive Metrics**: Calculate CTR, CVR, CPA, CPC, ROAS, ACOS, TACOS, and more
- **Flexible Date Selection**: Define custom lead-in, lead-out, and comparison periods
- **Interactive Visualizations**: Charts and graphs for performance comparison
- **Export Functionality**: Download results in CSV and Excel formats
- **Railway Deployment Ready**: Configured for easy deployment on Railway platform

## File Structure

```
amazon-data-analysis/
├── main.py                 # Main Streamlit application
├── data_processor.py       # Data processing and cleaning logic
├── calculations.py         # Metrics calculation functions
├── ui_components.py        # UI components and visualization
├── requirements.txt        # Python dependencies
├── railway.json           # Railway deployment configuration
└── README.md              # This file
```

## Required Input Files

The application expects four Excel files:

1. **Transaction Data**: Contains order/transaction information
   - Must include columns like: sales-channel, item-price, purchase-date, item-promotion-discount
   
2. **SP Campaign Data**: Sponsored Products campaign data
   - Should include: impressions, clicks, spend, sales, orders data
   
3. **SB Campaign Data**: Sponsored Brands campaign data
   - Should include: impressions, clicks, spend, sales, orders data
   
4. **SD Campaign Data**: Sponsored Display campaign data
   - Should include: impressions, clicks, spend, sales, orders data

## Installation and Setup

### Local Development

1. Clone or download the application files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run main.py
   ```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Railway will automatically detect the configuration from `railway.json`
3. The application will be deployed with the correct start command and port configuration

## Usage

1. **Upload Files**: Use the sidebar to upload all four required Excel files
2. **Data Processing**: The application will automatically process and combine the data
3. **Date Selection**: Choose your lead-in, lead-out, and any custom analysis periods
4. **View Results**: Analyze the calculated metrics in the results table and charts
5. **Export**: Download your results in CSV or Excel format

## Calculated Metrics

- **CTR (Click-Through Rate)**: (Clicks / Impressions) × 100
- **CVR (Conversion Rate)**: (Orders / Clicks) × 100
- **CPA (Cost Per Acquisition)**: Spend / Orders
- **CPC (Cost Per Click)**: Spend / Clicks
- **ROAS (Return on Ad Spend)**: Sales / Spend
- **ACOS (Advertising Cost of Sales)**: (Spend / Sales) × 100
- **TACOS (Total Advertising Cost of Sales)**: (Spend / Total Sales) × 100

## Data Processing Features

- Filters out Non-Amazon sales channels from transaction data
- Extracts dates from timestamps for proper grouping
- Handles various campaign data column naming conventions
- Combines and aggregates data by date
- Calculates net revenue (revenue - promotions)
- Handles missing data gracefully

## Troubleshooting

### Common Issues

1. **File Upload Errors**: Ensure your Excel files have the expected column names
2. **Date Format Issues**: The application expects standard date formats in Excel
3. **Missing Columns**: Check that your files contain the required columns for calculations

### Column Name Variations

The application handles various column naming conventions:
- Dates: "date", "purchase-date", etc.
- Orders: "orders", "7 day total orders", "14 day total orders", etc.
- Spend: "spend", "cost", "campaign-spend"
- Sales: "sales", "revenue", "attributed-sales"

## Contributing

To extend or modify the application:

1. **data_processor.py**: Modify data cleaning and processing logic
2. **calculations.py**: Add new metrics or modify existing calculations
3. **ui_components.py**: Update the user interface or add new visualizations
4. **main.py**: Modify the main application flow

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify your input file formats match the expected structure
3. Review the error messages in the Streamlit interface

## License

This project is provided as-is for Amazon data analysis purposes.