import pandas as pd

def load_sales_file(file):
    if file.name.endswith(".csv"):
        try:
            df = pd.read_csv(file, engine="python")
        except MemoryError:
            chunks = pd.read_csv(file, chunksize=500000, engine="python")
            df = pd.concat(chunks, ignore_index=True)
    else:
        df = pd.read_excel(file)
    df.columns = df.columns.str.lower().str.strip()
    df = df.dropna(how="all")
    return df
