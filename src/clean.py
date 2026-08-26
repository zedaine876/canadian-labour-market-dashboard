import pandas as pd
from pathlib import Path

# Paths are resolved relative to this file, so the script runs from any CWD.
PROJECT_ROOT = Path(__file__).parent.parent
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "14100460-eng" / "14100460.csv"
CLEAN_PATH = PROJECT_ROOT / "data" / "clean" / "labour_tidy.csv"

#Creating pandas df
df = pd.read_csv(RAW_PATH)


## Cleaning data.

#Filtering to get rid of duplicates
df = df[(df['Statistics'] == "Estimate")
            & (df['Data type'] == 'Seasonally adjusted')
            ]

#Simplifying city names
city_mapping = {
    'Montréal, Quebec' : 'Montreal',
    'Toronto, Ontario' : 'Toronto',
    'Vancouver, British Columbia' : 'Vancouver'
}
df['City'] = df['GEO'].map(city_mapping)

#Guard against unmapped geographies: any GEO not in city_mapping becomes NaN.
unmapped = sorted(df.loc[df['City'].isna(), 'GEO'].unique())
if unmapped:
    print(f"Warning: dropping {len(unmapped)} unmapped geographies: {unmapped}")
df = df.dropna(subset=['City'])

#Setting date data type
df['date'] = pd.to_datetime(df['REF_DATE'])

wide = df.pivot_table(
    index = ['date', 'City'],
    columns = 'Labour force characteristics',
    values="VALUE"
).reset_index()

wide = wide.rename(columns={
    'Population': 'population',
    'Labour force': 'labour_force',
    'Employment': 'employment',
    'Unemployment': 'unemployment',
    'Unemployment rate': 'unemployment_rate',
    'Participation rate': 'participation_rate',
    'Employment rate': 'employment_rate',
})

wide.columns.name = None

#Ensure the output directory exists on a fresh clone.
CLEAN_PATH.parent.mkdir(parents=True, exist_ok=True)
wide.to_csv(CLEAN_PATH, index=False)

print(wide.shape)
print(wide.columns.tolist())
print(wide.head())
