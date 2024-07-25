import matplotlib.pyplot as plt
import geopandas as gpd
import folium
from IPython.display import display
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import geopandas as gpd
import folium
import matplotlib.colors as mcolors
import branca.colormap as cm

def plot_map(data, color_col, radius_col, radius_scale=10):
    '''
    Plots an interactive map of Goettingen and sets location markers according to the 'longitude' and 'latitude' column in the given dataframe. 
    The appearance of the location marker can be adjusted in radius and color by other columns in the given dataframe. 
    The radius scale can also be adjusted separately.

    Parameters
    ----------
    data : pandas.DataFrame
        The dataframe containing the data to be plotted. Must (!) contain longitude and latitude column.
    color_col : str
        The name of the column in the dataframe to use for color.
    radius_col : str
        The name of the column in the dataframe to use for radius.
    radius_scale : int, optional
    '''
    # hardcode Goettingen coordinates
    goe_lat = 51.5322
    goe_long = 9.9368

    if 'longitude' not in data.columns:
        longitude_col = data.columns[~data.columns.str.find('longitude').values.astype(bool)][0]
        print(f'Use column {longitude_col} for the longitude coordinate.')
    else:
        longitude_col = 'longitude'
    if 'latitude' not in data.columns:
        latitude_col = data.columns[~data.columns.str.find('latitude').values.astype(bool)][0]
        print(f' Use the column {latitude_col} for the latitude coordinate.')        
    else:
        latitude_col = 'latitude'
        
    # create a GeoDataFrame
    gdf = gpd.GeoDataFrame(data, geometry=gpd.points_from_xy(data[longitude_col], data[latitude_col]), crs="EPSG:4326")

    # initialize the map centered around the coordinates
    m = folium.Map(location=[goe_lat, goe_long], zoom_start=15)
    
    # choose a colormap
    cmap = plt.cm.coolwarm
    # normalize the values
    norm = mcolors.Normalize(vmin=gdf[color_col].min(), vmax=gdf[color_col].max())
    scalar_map = plt.cm.ScalarMappable(norm=norm, cmap=cmap)

    # function to map values to colors
    def map_value_to_color(value):
        return mcolors.to_hex(scalar_map.to_rgba(value))

    # map the normalized values to colors
    gdf['radius_norm'] = (gdf[radius_col]-gdf[radius_col].min())/(gdf[radius_col].max()-gdf[radius_col].min())
    for idx, row in gdf.iterrows():
        popup_content = "<b>Details:</b><br>"
        for key, value in row.items():
            if key not in ['latitude', 'longitude', 'geometry', 'color', 'radius_norm']:
                popup_content += f"<b>{key.capitalize()}:</b> {value}<br>"
        folium.CircleMarker(
            location=[row[latitude_col], row[longitude_col]],
            radius=5+radius_scale*row['radius_norm'],  
            color=map_value_to_color(row[color_col]),
            fill=True,
            fill_color=map_value_to_color(row[color_col]),
            fill_opacity=0.9,
            popup=popup_content
        ).add_to(m)

    # create a branca colormap object
    colormap = cm.LinearColormap(
        colors=[cmap(i) for i in range(cmap.N)],
        vmin=gdf[color_col].min(),
        vmax=gdf[color_col].max(),
        caption= color_col
    )

    # add the colormap as a legend
    colormap.add_to(m)

    display(m)