import logging
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List
from sat_sight.core.state import AgentState

logger = logging.getLogger(__name__)


def extract_coordinates(query: str) -> Optional[Tuple[float, float]]:
    """Extract latitude and longitude from query text."""
    
    coord_pattern = r'(-?\d+\.?\d*)[,\s]+(-?\d+\.?\d*)'
    match = re.search(coord_pattern, query)
    
    if match:
        try:
            lat = float(match.group(1))
            lon = float(match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        except ValueError:
            pass
    
    return None


def extract_location_names(query: str) -> List[str]:
    """Extract location names from query."""
    
    query_lower = query.lower()
    
    locations = {
        "paris": ["paris", "31udq"],
        "france": ["france", "31udq", "32tlt"],
        "switzerland": ["switzerland", "31ufs"],
        "austria": ["austria", "31ufs"],
        "germany": ["germany", "stuttgart", "32umu"],
        "stuttgart": ["stuttgart", "32umu"],
        "poland": ["poland", "34uda"],
        "czech": ["czech", "33uuu"],
        "alps": ["alps", "32tlt"],
        "amazon": ["amazon", "brazil", "20llq", "20llr", "20lmq", "20lmr"],
        "brazil": ["brazil", "20llq", "20llr", "20lmq", "20lmr"],
        "california": ["california", "10tfk", "10tgk", "11ska", "11skb"],
        "sahel": ["sahel", "31pet", "32pnt", "33pvn", "34pea"],
        "africa": ["africa", "sahel"]
    }
    
    found_locations = []
    for loc_key, loc_aliases in locations.items():
        if any(alias in query_lower for alias in loc_aliases):
            found_locations.append(loc_key)
    
    return found_locations


def extract_land_class(query: str) -> Optional[str]:
    """Extract land use class from query."""
    
    query_lower = query.lower()
    
    class_keywords = {
        "forest": ["forest", "tree", "woodland"],
        "agricultural": ["agricultural", "farm", "crop"],
        "river": ["river", "stream", "water"],
        "lake": ["lake", "sea"],
        "residential": ["residential", "urban", "city", "town"],
        "industrial": ["industrial", "factory"],
        "highway": ["highway", "road"],
        "pasture": ["pasture", "grassland"]
    }
    
    for land_class, keywords in class_keywords.items():
        if any(kw in query_lower for kw in keywords):
            return land_class
    
    return None


def search_by_location(location_names: List[str], land_class: Optional[str] = None) -> List[Dict]:
    """Search enriched metadata for images matching location and land class."""
    
    metadata_file = Path("data/metadata/eurosat_metadata_real_coords.jsonl")
    
    if not metadata_file.exists():
        logger.warning(f"Enriched metadata not found: {metadata_file}")
        return []
    
    matching_images = []
    
    with open(metadata_file, 'r') as f:
        for line in f:
            entry = json.loads(line)
            
            location = entry.get("location", {})
            region = location.get("region", "").lower()
            country = location.get("country", "").lower()
            tile = entry.get("coordinates", {}).get("source_tile", "").lower()
            
            location_match = False
            for loc_name in location_names:
                loc_lower = loc_name.lower()
                if (loc_lower in region or 
                    loc_lower in country or 
                    loc_lower in tile or
                    region.startswith(loc_lower) or
                    country.startswith(loc_lower)):
                    location_match = True
                    break
            
            if not location_match:
                continue
            
            if land_class:
                entry_class = entry.get("class", "").lower()
                if land_class not in entry_class and entry_class not in land_class:
                    continue
            
            matching_images.append({
                "filename": entry.get("image_path"),
                "class": entry.get("class"),
                "location": location.get("region"),
                "country": location.get("country"),
                "coordinates": entry.get("coordinates"),
                "metadata": entry
            })
    
    return matching_images


def geo_node(state: AgentState) -> Dict[str, Any]:
    """Geo Agent: Handles location-based queries and geographic data retrieval."""
    
    logger.info("Geo Agent invoked")
    
    query = state.get("query", "")
    
    coordinates = extract_coordinates(query)
    
    location_names = extract_location_names(query)
    
    land_class = extract_land_class(query)
    
    geo_data = None
    retrieved_images = []
    
    if coordinates:
        lat, lon = coordinates
        logger.info(f"Extracted coordinates: {lat}, {lon}")
        geo_data = {
            "latitude": lat,
            "longitude": lon,
            "type": "point"
        }
    elif location_names:
        logger.info(f"Extracted location names: {location_names}")
        logger.info(f"Land class filter: {land_class}")
        
        matching_images = search_by_location(location_names, land_class)
        
        logger.info(f"Found {len(matching_images)} images matching location query")
        
        if matching_images:
            retrieved_images = matching_images[:10]
            
            geo_data = {
                "location_names": location_names,
                "land_class": land_class,
                "type": "location_search",
                "results_count": len(matching_images)
            }
            
            if retrieved_images:
                logger.info(f"Sample results:")
                for img in retrieved_images[:3]:
                    logger.info(f"  - {img['filename']}: {img['class']} in {img['location']}")
    else:
        logger.info("No coordinates or location names found in query")
    
    return {
        "current_agent": "geo_agent",
        "next_agent": "memory_agent",  # Route to memory before reasoning
        "geo_data": geo_data,
        "retrieved_images": retrieved_images
    }
