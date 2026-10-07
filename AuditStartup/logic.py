import pandas as pd
import io

def run_internal_audit():
    # 1. CREATE DATA FROM SCRATCH (Simulating a Tally/Excel Export)
    # Notice: 'Item_B' has a NaN (Missing) Price, and 'Item_C' has a negative Stock.
    raw_data = """Item_Name,Price,Stock_Level,Category
    Item_A,150,20,Electronics
    Item_B,,15,Hardware
    Item_C,500,-5,Electronics
    Item_D,250,10,Hardware
    Item_A,150,20,Electronics""" # Item_A is a duplicate
    
    # Load this text string into a DataFrame
    df = pd.read_csv(io.StringIO(raw_data))
    
    print("--- 🔍 STARTUP AUDIT ENGINE ACTIVE ---")
    print(f"Analyzing {len(df)} records...\n")

    # 2. THE AUDIT LOGIC (Your Business Value)
    
    # Check A: Missing Data (Revenue Leak)
    missing = df.isnull().sum().sum()
    
    # Check B: Inventory Errors (Negative Stock)
    low_stock_errors = df[df['Stock_Level'] < 0]['Item_Name'].tolist()
    
    # Check C: Duplicate Entries (Wasteful Data)
    duplicates = df.duplicated().sum()

    # 3. GENERATE THE REPORT
    print("--- 📊 AUDIT REPORT SUMMARY ---")
    print(f"1. Missing Values: {missing} (Action: Check Item_B Price)")
    print(f"2. Negative Stock: {low_stock_errors} (Action: Recount Inventory)")
    print(f"3. Duplicate Rows: {duplicates} (Action: Clean Database)")
    print("-------------------------------")
    print("Status: AUDIT COMPLETE")

# CALL THE FUNCTION
run_internal_audit()
