import pandas as pd

def sample_retail_sales():
    return pd.DataFrame({
        "OrderID": [101, 102, 103, 104, 101, 105, 106, 107, 108, 109, 105, 110],
        "Order Date": ["January 15, 2024", "January 18, 2024", "January 20, 2024", "January 22, 2024", "January 15, 2024", "February 01, 2024", "February 05, 2024", "February 10, 2024", "February 14, 2024", "February 18, 2024", "February 01, 2024", "February 20, 2024"],
        "Customer Name": ["Alice Smith", "Bob Jones", "Charlie Brown", "Diana Prince", "Alice Smith", "Evan Wright", "Fiona Gallagher", "George Clark", "Hannah Abbott", "Ian Malcolm", "Evan Wright", "Julia Roberts"],
        "Region": ["North", "South", "East", "West", "North", "South", "East", "North", "West", "South", "South", "East"],
        "Category": ["Technology", "Furniture", "Office Supplies", "Technology", "Technology", "Furniture", "Office Supplies", "Technology", "Furniture", "Office Supplies", "Furniture", "Technology"],
        "Sales": [1200.5, 450.0, 320.0, 890.2, 1200.5, 330.0, 150.4, 2100.0, 540.0, 670.0, 330.0, 1450.0],
        "Profit": [240.0, 45.0, 30.0, 120.0, 240.0, 50.0, 15.0, 420.0, 110.0, 90.0, 50.0, 290.0]
    })

def sample_hr_records():
    return pd.DataFrame({
        "EmpID": [1001, 1002, 1003, 1004, 1005, 1006, 1001, 1007, 1008, 1009],
        "Employee Name": ["John Doe", "Jane Smith", "Robert Fox", "Emily Davis", "Michael Brown", "Sarah Wilson", "John Doe", "David Miller", "Laura Taylor", "James Anderson"],
        "Join Date": ["January 10, 2022", "March 15, 2022", "May 20, 2022", "June 11, 2022", "July 01, 2022", "August 19, 2022", "January 10, 2022", "September 05, 2022", "October 12, 2022", "November 01, 2022"],
        "Department": ["Engineering", "Marketing", "HR", "Sales", "Engineering", "Finance", "Engineering", "Sales", "HR", "Marketing"],
        "Salary": [95000, 68000, 55000, 72000, 98000, 110000, 95000, 69000, 56000, 75000],
        "Performance Score": [4.5, 3.9, 4.1, 4.7, 4.8, 4.2, 4.5, 3.8, 4.0, 4.3]
    })

def sample_global_airports():
    return pd.DataFrame({
        "Airport Code": ["JFK", "LAX", "LHR", "HND", "CDG", "SYD", "FRA", "DXB", "SIN", "BOM"],
        "City": ["New York", "Los Angeles", "London", "Tokyo", "Paris", "Sydney", "Frankfurt", "Dubai", "Singapore", "Mumbai"],
        "Country": ["United States", "United States", "United Kingdom", "Japan", "France", "Australia", "Germany", "United Arab Emirates", "Singapore", "India"],
        "Latitude": [40.64, 33.94, 51.47, 35.54, 49.00, -33.94, 50.03, 25.25, 1.36, 19.08],
        "Longitude": [-73.77, -118.40, -0.45, 139.77, 2.54, 151.17, 8.57, 55.36, 103.99, 72.87],
        "Annual Passengers (Millions)": [62.5, 75.0, 61.6, 75.1, 67.4, 38.3, 59.4, 86.6, 68.3, 48.5]
    })

def sample_india_airports():
    return pd.DataFrame({
        "Airport Code": ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD", "AMD", "COK", "GOI", "PNQ", "TRV", "GAU"],
        "City": ["New Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Ahmedabad", "Kochi", "Goa", "Pune", "Thiruvananthapuram", "Guwahati"],
        "State": ["Delhi", "Maharashtra", "Karnataka", "Tamil Nadu", "West Bengal", "Telangana", "Gujarat", "Kerala", "Goa", "Maharashtra", "Kerala", "Assam"],
        "Latitude": [28.5562, 19.0896, 13.1986, 12.9941, 22.6547, 17.2403, 23.0770, 10.1520, 15.3808, 18.5822, 8.4821, 26.1061],
        "Longitude": [77.1000, 72.8656, 77.7066, 80.1709, 88.4467, 78.4294, 72.6347, 76.4019, 73.8313, 73.9197, 76.9200, 91.5859],
        "Annual Passengers (Millions)": [65.3, 49.8, 33.6, 22.1, 19.9, 21.0, 11.5, 10.2, 8.4, 9.1, 4.2, 5.8]
    })

SAMPLE_OPTIONS = {
    "1. Retail Sales & Orders": sample_retail_sales,
    "2. HR Employee Records": sample_hr_records,
    "3. Global Airports Data": sample_global_airports,
    "4. Major Indian Airports & Cities": sample_india_airports
}