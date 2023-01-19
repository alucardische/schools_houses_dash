import googlemaps
import pandas as pd

gmaps_client = googlemaps.Client(key='AIzaSyAVp3N1Tst_7K5zl9uPB9JFzf2t_d6CCdU')
schools_meta = pd.read_csv('2018-2019/england_school_information.csv')
best_schools = pd.read_csv('https://github.com/alucardische/datasets/raw/main/oxbridge_schools.csv')
schools_meta['school_clean'] = schools_meta['SCHNAME'].str.replace('\'', '').str.replace('The ', '').str.replace('Mathematics', 'Maths').apply(lambda x: x.split(',')[0].strip())
best_schools['school_clean'] = best_schools['School'].str.replace('’', '').str.replace('\'', '').str.replace('The ', '').str.replace('Mathematics', 'Maths').apply(lambda x: x.split(',')[0].strip())
merged = pd.merge(best_schools, schools_meta, left_on='school_clean', right_on='school_clean', how='left')


def get_lat_lng(name):
  try:
    geocode_result = gmaps_client.geocode(name)
    location = geocode_result[0]['geometry']['location']
    return location['lat'], location['lng']
  except:
    return None, None

# for index, row in merged.iterrows():
#   lat, lng = get_lat_lng(row['School'] + ', United Kingdom')
#   merged.loc[index, 'lat'] = lat
#   merged.loc[index, 'lng'] = lng

merged = pd.read_csv('merged.csv')
