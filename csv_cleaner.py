import pandas as pd

df = pd.read_csv(
    r"C:\Users\Acer\Desktop\Temp-Works\DAQ\SmartFarm\EcoCrop_DB.csv",
    encoding='ISO-8859-1'  # or 'cp1252' if needed
)

light_map = {
    'very bright': 0,
    'clear skies': 200,
    'cloudy skies': 500,
    'light shade': 800,
    'dark': 1023
}


def rainfall_to_rh(rainfall):
    try:
        r = float(rainfall)
        r = max(50, min(r, 9900))  # Clamp to [50, 9900]
        return round(20 + ((r - 50) / (9900 - 50)) * (90 - 20), 2)
    except:
        return None


def parse_light(val):
    return light_map.get(val.strip().lower(), None) if isinstance(val, str) else None


# Apply rainfall to RH conversion
df['RHMIN'] = df['RMIN'].apply(rainfall_to_rh)
df['RHMAX'] = df['RMAX'].apply(rainfall_to_rh)

cleaned = pd.DataFrame({
    'scientific_name': df['ScientificName'].str.strip(),
    'common_name': df['COMNAME'].str.strip(),
    'optimal_temperature_min': pd.to_numeric(df['TMIN'], errors='coerce'),
    'optimal_temperature_max': pd.to_numeric(df['TMAX'], errors='coerce'),
    'optimal_humidity_min': df['RHMIN'],
    'optimal_humidity_max': df['RHMAX'],
    'optimal_light_min': df['LIMX'].apply(parse_light),
    'optimal_light_max': df['LIMN'].apply(parse_light),
    'source': "http://ecoport.org/perl/ecoport15.pl?searchType=entityDisplay&entityId=" + df['EcoPortCode'].astype(str)
})

cleaned = cleaned.dropna(subset=[
    'common_name', 'scientific_name',
    'optimal_temperature_min', 'optimal_temperature_max',
    'optimal_humidity_min', 'optimal_humidity_max',
    'optimal_light_min', 'optimal_light_max'
])

cleaned.to_csv(r"C:\Users\Acer\Desktop\Temp-Works\DAQ\SmartFarm\cleaned_crops.csv", index=False)
