# EOmaps example 7: Using geopandas - interactive shapes!

from eomaps import Maps, MapsGrid
import pandas as pd
import numpy as np
import geopandas as gpd

# geopandas is used internally... the import is just here to show that!


# ----------- create some example-data
lon, lat = np.meshgrid(np.linspace(-180, 180, 25), np.linspace(-90, 90, 25))
data = pd.DataFrame(
    dict(lon=lon.flat, lat=lat.flat, data=np.sqrt(lon**2 + lat**2).flat)
)

# ----------- setup some maps objects and assign datasets and the plot-crs
mg = MapsGrid(1, 2, crs=[4326, Maps.CRS.Orthographic(45, 45)], figsize=(10, 5))
mg.m_0_0.set_data(data=data.sample(100), x="lon", y="lat", crs=4326, parameter="data")

mg.m_0_1.set_data(data=data, x="lon", y="lat", crs=4326)

mg.add_feature.preset.ocean()

# fetch the data (incl. metadata) for the "admin_0_countries" feature
countries = mg.add_feature.cultural.admin_0_countries.get_gdf(scale=50)
mg.add_gdf(
    countries,
    picker_name="countries",
    pick_method="contains",
    val_key="NAME",
    fc="none",
    ec="k",
    lw=0.5,
)

mg.set_shape.rectangles(radius=3, radius_crs=4326)
mg.plot_map(alpha=0.75, ec=(1, 1, 1, 0.5), pick_distance=25)

for m in mg:
    # attach a callback to highlite the rectangles
    m.cb.pick.attach.mark(
        permanent=False, shape="rectangles", fc="none", ec="b", lw=2, zorder=5
    )

    # attach a callback to highlite the countries and indicate the names
    m.cb.pick["countries"].attach.highlight_geometry(fc="r", ec="k", lw=0.5)
    m.cb.pick["countries"].attach.annotate(text=lambda val, **kwargs: str(val))


mg.share_pick_events()  # share default pick events
mg.share_pick_events("countries")  # share the events of the "countries" picker
mg.m_0_1.add_logo()
