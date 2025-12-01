"""
Manager for geospatial data retrieval (e.g., from OpenStreetMap).
Provides functions to query location-specific information.
"""
import logging
import osmnx as ox
from typing import Dict, Any, Optional, List
import geopandas as gpd
import pandas as pd

logger = logging.getLogger(__name__)

class GeoManager:
    """
    A class to manage geospatial data retrieval (e.g., from OpenStreetMap).
    Provides functions to query location-specific information.
    """
    def __init__(self, default_radius_meters: int = 1000):
        """
        Initializes the Geo Manager.

        Args:
            default_radius_meters (int): Default radius in meters for geospatial queries if not specified.
        """
        self.default_radius_meters = default_radius_meters
        ox.settings.cache_folder = "data/osm_cache" # Optional: cache OSM data locally
        ox.settings.use_cache = True # Use cache to avoid repeated API calls
        logger.info("GeoManager initialized with OSMnx.")

    def query_location_info(self, location_hint: str, radius_meters: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Queries OpenStreetMap for information around a location hint (address, place name, or coordinates).

        Args:
            location_hint (str): A string representing the location (e.g., "Paris, France", "48.8566, 2.3522", "Tropical Rainforest near Manaus").
                                For satellite imagery, this might come from image metadata (e.g., 'region_hint': 'Andalusia, Spain') or filename.
            radius_meters (int, optional): Radius in meters around the central point to query. Uses default if not provided.

        Returns:
            Optional[Dict[str, Any]]: Dictionary containing retrieved geospatial information like nearby features,
                                    elevation (if available via other means), land use, etc.
                                    Returns None if no data is found or an error occurs.
        """
        radius = radius_meters or self.default_radius_meters
        logger.debug(f"GeoManager: Querying OSM for location: '{location_hint}' within {radius}m radius.")

        try:
            geocode_result = ox.geocoder.geocode(query=location_hint)
            if not geocode_result or len(geocode_result) < 2:
                 logger.warning(f"GeoManager: Could not geocode location hint: '{location_hint}'.")
                 return None

            lat, lon = geocode_result
            logger.debug(f"GeoManager: Geocoded location '{location_hint}' to ({lat}, {lon}).")

            point = (lat, lon)

            try:
                tags = {'highway': True} # Example: get highways
                gdf_roads = ox.features.features_from_point(center_point=point, tags=tags, dist=radius)
                road_info = gdf_roads[['highway', 'name', 'length']].to_dict('records') if not gdf_roads.empty else []
            except Exception as e:
                 logger.warning(f"GeoManager: Error querying OSM for roads near '{location_hint}': {e}")
                 road_info = []

            try:
                tags = {'landuse': True, 'building': True} # Example: get landuse and buildings
                gdf_landuse = ox.features.features_from_point(center_point=point, tags=tags, dist=radius)
                landuse_info = gdf_landuse[['landuse', 'building', 'name']].to_dict('records') if not gdf_landuse.empty else []
            except Exception as e:
                 logger.warning(f"GeoManager: Error querying OSM for landuse/buildings near '{location_hint}': {e}")
                 landuse_info = []

            try:
                tags = {'boundary': 'protected_area', 'protection_title': True}
                gdf_protected = ox.features.features_from_point(center_point=point, tags=tags, dist=radius)
                protected_info = gdf_protected[['protection_title', 'name', 'operator']].to_dict('records') if not gdf_protected.empty else []
            except Exception as e:
                 logger.warning(f"GeoManager: Error querying OSM for protected areas near '{location_hint}': {e}")
                 protected_info = []

            try:
                tags = {'natural': 'water', 'water': True}
                gdf_water = ox.features.features_from_point(center_point=point, tags=tags, dist=radius)
                water_info = gdf_water[['natural', 'water', 'name']].to_dict('records') if not gdf_water.empty else []
            except Exception as e:
                 logger.warning(f"GeoManager: Error querying OSM for water bodies near '{location_hint}': {e}")
                 water_info = []

            try:
                tags = {'amenity': True}
                gdf_amenities = ox.features.features_from_point(center_point=point, tags=tags, dist=radius)
                amenity_info = gdf_amenities[['amenity', 'name', 'operator']].to_dict('records') if not gdf_amenities.empty else []
            except Exception as e:
                 logger.warning(f"GeoManager: Error querying OSM for amenities near '{location_hint}': {e}")
                 amenity_info = []


            geo_data = {
                "queried_location_hint": location_hint,
                "queried_center_coordinates": {"lat": lat, "lon": lon},
                "query_radius_meters": radius,
                "nearby_roads": road_info,
                "nearby_landuse_or_buildings": landuse_info,
                "nearby_protected_areas": protected_info,
                "nearby_water_bodies": water_info,
                "nearby_amenities": amenity_info,
            }

            logger.info(f"GeoManager: Retrieved geospatial data for location '{location_hint}'. Found {len(road_info)} roads, {len(landuse_info)} landuse/buildings, {len(protected_info)} protected areas, {len(water_info)} water bodies, {len(amenity_info)} amenities.")
            return geo_data

        except Exception as e:
            logger.error(f"Error querying geospatial data for '{location_hint}': {e}")
            import traceback
            traceback.print_exc()
            return None

    def query_elevation(self, lat: float, lon: float) -> Optional[float]:
        """
        Queries elevation for a specific latitude/longitude.
        This requires a different service than OSM (e.g., SRTM via NASA Earthdata or other DEM APIs).
        This is a placeholder/example. Implementation depends on the chosen elevation API.
        Requires API key setup for services like NASA Earthdata.
        """
        logger.warning("GeoManager: Elevation query requested, but direct implementation requires external API (e.g., NASA Earthdata, OpenTopography).")
        return None # For now, return None as it requires a specific API setup

