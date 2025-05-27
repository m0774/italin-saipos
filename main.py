import json
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from math import radians, cos, sin, pi
from lxml import etree

# ✅ Ponto de origem definido manualmente
origin_point = (-23.97024634568765, -46.309996685162425)  # (lat, lng)

max_radius_km = 10  # ✅ Número de anéis desejado

def create_circle(center, radius_km, num_points=72):
    lat, lng = center
    coords = []
    for i in range(num_points):
        angle = 2 * pi * i / num_points
        dx = radius_km * cos(angle)
        dy = radius_km * sin(angle)
        delta_lat = dy / 110.574  
        delta_lng = dx / (111.320 * cos(radians(lat)))  
        coords.append((lng + delta_lng, lat + delta_lat))
    coords.append(coords[0])  
    return Polygon(coords)

def add_polygon_to_kml(name, geom, doc):
    if geom.is_empty:
        return
    if isinstance(geom, Polygon):
        placemark = polygon_to_kml(name, geom)
        doc.append(placemark)
    elif isinstance(geom, MultiPolygon):
        for idx, poly in enumerate(geom.geoms):
            placemark = polygon_to_kml(f"{name} - parte {idx+1}", poly)
            doc.append(placemark)

def polygon_to_kml(name, polygon):
    kml = etree.Element("Placemark")
    name_elem = etree.SubElement(kml, "name")
    name_elem.text = name
    poly_elem = etree.SubElement(kml, "Polygon")
    outer = etree.SubElement(poly_elem, "outerBoundaryIs")
    lr = etree.SubElement(outer, "LinearRing")
    coords_elem = etree.SubElement(lr, "coordinates")
    
    coords_text = " ".join([f"{x},{y},0" for x, y in polygon.exterior.coords])
    coords_elem.text = coords_text
    return kml

with open('objeto.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

kml_root = etree.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
doc = etree.SubElement(kml_root, "Document")

for feature in data:
    geom = feature['geometry']
    name = feature['properties'].get('desc_store_district', 'Sem nome')

    if geom['type'] == 'Polygon':
        coords = geom['coordinates'][0]
        polygon = Polygon(coords)
        polygon = orient(polygon)

        add_polygon_to_kml(name, polygon, doc)

        center = origin_point

        for r in range(1, max_radius_km + 1):
            circle = create_circle(center, r)
            intersec = polygon.intersection(circle)

            if intersec.is_empty:
                print(f"❌ Raio de {r} km não cabe, parando.")
                break

            area_deg = intersec.area
            area_km2 = area_deg * (110.574 ** 2)

            name_with_area = f"Raio de {r}km - {area_km2:.2f} km²"
            add_polygon_to_kml(name_with_area, intersec, doc)
            print(f"✅ {name_with_area} adicionado.")

tree = etree.ElementTree(kml_root)
tree.write("final_kml_manual_origin.kml", pretty_print=True, xml_declaration=True, encoding="UTF-8")

print("✅ KML gerado: final_kml_manual_origin.kml")
