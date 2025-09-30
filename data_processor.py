import pandas as pd
import numpy as np
from datetime import datetime
import io

class DataProcessor:
    
    def process_transaction_data(self, file_bytes):
        """Process transaction data file from bytes"""
        # Use openpyxl engine and only read necessary columns for speed
        # Read only the columns we need
        df = pd.read_excel(
            io.BytesIO(file_bytes),
            engine='openpyxl',
            usecols=['sales-channel', 'purchase-date', 'order-status', 'quantity', 'item-price', 'item-promotion-discount']
        )
        
        print(f"Original data: {len(df)} rows")
        
        # Filter early - this is the biggest speedup
        mask = (df['sales-channel'] == 'Amazon.com') & (df['order-status'] == 'Shipped')
        df = df[mask]
        print(f"After filters: {len(df)} rows")
        
        # Fast date conversion using pandas built-in
        df['date'] = pd.to_datetime(df['purchase-date'], errors='coerce').dt.date
        df = df.dropna(subset=['date'])
        print(f"After date conversion: {len(df)} rows")
        
        # Fill NaN and convert to numeric in one step
        df[['item-price', 'item-promotion-discount', 'quantity']] = df[['item-price', 'item-promotion-discount', 'quantity']].fillna(0).astype(float)
        
        # Group by date - single operation
        result = df.groupby('date', as_index=False).agg({
            'quantity': 'sum',
            'item-price': 'sum',
            'item-promotion-discount': 'sum'
        })
        
        # Count orders separately
        orders_count = df.groupby('date').size().reset_index(name='orders')
        result = result.merge(orders_count, on='date')
        
        # Rename and calculate
        result.columns = ['date', 'total_units', 'revenue', 'item_promotion_discount', 'orders']
        result['net_revenue'] = result['revenue'] - result['item_promotion_discount']
        
        print(f"✅ Transaction data processed: ${result['revenue'].sum():.2f} total revenue")
        
        return result
    
    def process_campaign_data(self, sp_bytes, sb_bytes, sd_bytes):
        """Process all campaign data files from bytes"""
        all_data = []
        
        # Process SP data
        if sp_bytes:
            sp_df = pd.read_excel(
                io.BytesIO(sp_bytes),
                engine='openpyxl',
                usecols=['Date', 'Impressions', 'Clicks', 'Spend', '7 Day Total Orders (#)', '7 Day Total Sales ']
            )
            sp_df['date'] = self._convert_excel_date_vectorized(sp_df['Date'])
            sp_processed = sp_df.groupby('date', as_index=False).agg({
                'Impressions': 'sum',
                'Clicks': 'sum',
                'Spend': 'sum',
                '7 Day Total Orders (#)': 'sum',
                '7 Day Total Sales ': 'sum'
            })
            sp_processed.columns = ['date', 'impressions', 'clicks', 'campaign_spend', 'campaign_orders', 'campaign_sales']
            all_data.append(sp_processed)
        
        # Process SB data
        if sb_bytes:
            sb_df = pd.read_excel(
                io.BytesIO(sb_bytes),
                engine='openpyxl',
                usecols=['Date', 'Impressions', 'Clicks', 'Spend', '14 Day Total Orders (#)', '14 Day Total Sales ']
            )
            sb_df['date'] = self._convert_excel_date_vectorized(sb_df['Date'])
            sb_processed = sb_df.groupby('date', as_index=False).agg({
                'Impressions': 'sum',
                'Clicks': 'sum',
                'Spend': 'sum',
                '14 Day Total Orders (#)': 'sum',
                '14 Day Total Sales ': 'sum'
            })
            sb_processed.columns = ['date', 'impressions', 'clicks', 'campaign_spend', 'campaign_orders', 'campaign_sales']
            all_data.append(sb_processed)
        
        # Process SD data
        if sd_bytes:
            sd_df = pd.read_excel(
                io.BytesIO(sd_bytes),
                engine='openpyxl',
                usecols=['Date', 'Impressions', 'Clicks', 'Spend', '14 Day Total Orders (#)', '14 Day Total Sales ']
            )
            sd_df['date'] = self._convert_excel_date_vectorized(sd_df['Date'])
            sd_processed = sd_df.groupby('date', as_index=False).agg({
                'Impressions': 'sum',
                'Clicks': 'sum',
                'Spend': 'sum',
                '14 Day Total Orders (#)': 'sum',
                '14 Day Total Sales ': 'sum'
            })
            sd_processed.columns = ['date', 'impressions', 'clicks', 'campaign_spend', 'campaign_orders', 'campaign_sales']
            all_data.append(sd_processed)
        
        # Combine all campaign data
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            
            # Sum by date
            result = combined.groupby('date', as_index=False).agg({
                'impressions': 'sum',
                'clicks': 'sum', 
                'campaign_spend': 'sum',
                'campaign_orders': 'sum',
                'campaign_sales': 'sum'
            })
            
            print(f"✅ Campaign data processed: ${result['campaign_spend'].sum():.2f} total spend")
            
            return result
        
        return pd.DataFrame()
    
    def _convert_excel_date_vectorized(self, date_series):
        """Convert Excel serial dates to Python dates using vectorization"""
        from datetime import datetime, timedelta
        excel_epoch = datetime(1899, 12, 30)
        
        # Vectorized conversion for numeric dates
        def convert_single(date_val):
            if isinstance(date_val, (int, float)):
                return (excel_epoch + timedelta(days=date_val)).date()
            else:
                return pd.to_datetime(date_val).date()
        
        return date_series.apply(convert_single)
    
    def combine_data(self, transaction_df, campaign_df):
        """Combine transaction and campaign data"""
        if transaction_df.empty and campaign_df.empty:
            return pd.DataFrame()
        
        # Merge on date
        if not transaction_df.empty and not campaign_df.empty:
            combined = pd.merge(transaction_df, campaign_df, on='date', how='outer')
        elif transaction_df.empty:
            combined = campaign_df.copy()
            # Add missing transaction columns with correct names
            combined['orders'] = 0
            combined['total_units'] = 0
            combined['revenue'] = 0
            combined['item_promotion_discount'] = 0
            combined['net_revenue'] = 0
        else:
            combined = transaction_df.copy()
            # Add missing campaign columns
            combined['impressions'] = 0
            combined['clicks'] = 0
            combined['campaign_orders'] = 0
            combined['campaign_spend'] = 0
            combined['campaign_sales'] = 0
        
        # Fill NaN with 0
        combined = combined.fillna(0)
        
        # Ensure correct column mapping - transaction columns should map to final names
        column_mapping = {}
        
        # If we have transaction columns with different names, map them
        if 'orders' not in combined.columns and any(col in combined.columns for col in ['orders']):
            pass  # orders is already correct
        
        # The transaction processor should output: orders, total_units, revenue, item_promotion_discount, net_revenue
        # The campaign processor should output: impressions, clicks, campaign_orders, campaign_spend, campaign_sales
        
        # Debug: print what columns we actually have
        print("Combined columns:", combined.columns.tolist())
        
        # Ensure all expected columns exist
        expected_columns = [
            'date', 'orders', 'total_units', 'revenue', 'item_promotion_discount', 'net_revenue',
            'impressions', 'clicks', 'campaign_orders', 'campaign_spend', 'campaign_sales'
        ]
        
        for col in expected_columns:
            if col not in combined.columns:
                combined[col] = 0
        
        return combined[expected_columns]