.# 🛍️ E-Commerce Intelligence Platform

A production-style business intelligence and machine learning platform
for analyzing e-commerce customer behavior, sales, products, inventory,
marketing performance and business risks.

## 🚀 Features

### 📊 Executive Dashboard
- Revenue tracking
- Profit analysis
- Order volume
- Average order value
- Regional performance
- Category performance
- Product performance

### 👤 Customer Intelligence
- Customer 360 profiles
- Purchase history
- Customer spending trends
- Customer segmentation
- Personalized recommendations

### ⚠️ Churn Prediction
- Customer churn probability
- High/medium/low risk classification
- Churn feature importance
- Retention recommendations

### 📈 Revenue Forecasting
- Historical revenue analysis
- Future revenue forecasting
- Configurable forecast horizon

### 🛍️ Product Intelligence
- Product revenue
- Product profitability
- Units sold
- Profit margin
- Product performance classification
- Category analysis

### 📦 Inventory Intelligence
- Stock monitoring
- Sales velocity
- Days of inventory remaining
- Stockout risk
- Reorder recommendations
- Overstock detection

### 📢 Marketing Analytics
- Marketing spend
- Campaign revenue
- Channel performance
- ROI analysis

### 💡 Action Center
Converts analytics into business recommendations such as:

- Reorder inventory
- Contact high-risk customers
- Review low-performing marketing channels
- Promote overstocked products
- Increase investment in strong-performing channels

### 📑 Business Reports
- Executive reports
- Monthly performance reports
- Product performance reports
- CSV downloads
- Excel downloads

---

# 🏗️ Architecture

```text
                    E-Commerce Data
                          │
             ┌────────────┼────────────┐
             │            │            │
         Customers      Orders      Products
             │            │            │
             └────────────┼────────────┘
                          │
                  Data Processing
                          │
             ┌────────────┼────────────┐
             │            │            │
        Customer ML   Product AI   Forecasting
             │            │            │
             └────────────┼────────────┘
                          │
                    Streamlit App
                          │
       ┌──────────┬───────┼────────┬──────────┐
       │          │       │        │          │
   Dashboard   Customer  Inventory Marketing  Reports
               360       AI        AI
                          │
                    Action Center
                          │
                  Business Decisions


