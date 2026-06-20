import pandas as pd
import sys

sys.stdout.reconfigure(encoding='utf-8')

def inspect_csv(file_path):
    print(f"=== Inspecting {file_path} ===")
    try:
        df = pd.read_csv(file_path)
        print("Columns:", list(df.columns))
        print("Shape:", df.shape)
        print("Unique Shops:")
        shops = df['Tên Shop'].unique()
        for s in shops:
            # Count products for this shop
            count = len(df[df['Tên Shop'] == s])
            print(f"  - {s}: {count} products")
    except Exception as e:
        print("Error:", e)

inspect_csv('khoa.csv')
inspect_csv('khoa2.csv')
