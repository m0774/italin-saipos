import json
from shapely.geometry import Point, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
from math import radians, cos, sin, pi
from lxml import etree

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

def point_to_kml(name, point_coords):
    kml = etree.Element("Placemark")
    name_elem = etree.SubElement(kml, "name")
    name_elem.text = name
    point_elem = etree.SubElement(kml, "Point")
    coords_elem = etree.SubElement(point_elem, "coordinates")
    
    coords_elem.text = f"{point_coords[1]},{point_coords[0]},0"
    return kml

with open('objeto.txt', 'r', encoding='utf-8') as f:
    data = json.load(f)

kml_root = etree.Element("kml", xmlns="http://www.opengis.net/kml/2.2")
doc = etree.SubElement(kml_root, "Document")

polygon = None

for feature in data:
    if feature['geometry']['type'] == 'Polygon':
        coords = feature['geometry']['coordinates'][0]
        polygon = Polygon(coords)
        polygon = orient(polygon)
        break 

if polygon is None:
    print("❌ Nenhum Polygon encontrado no arquivo.")
    exit()

print(f"✅ Polygon bounds (minx, miny, maxx, maxy): {polygon.bounds}")

origin_point = None
radius_modes = []

for feature in data:
    if feature['geometry']['type'] == 'Point':
        coords = feature['geometry']['coordinates']
        origin_point = (coords[0], coords[1]) 
        radius_modes = feature['properties'].get('radius_mode', [])
        break  

if origin_point is None:
    print("❌ Nenhum Point com radius_mode encontrado.")
    exit()

print(f"✅ Coordenadas originais do Point: {coords}")
print(f"✅ Origin Point (lat, lng): {origin_point}")

doc.append(point_to_kml("Centro do Raio", origin_point))
print(f"✅ Ponto de origem adicionado: {origin_point}")

for idx, item in enumerate(radius_modes):
    radius = item.get('radius')
    delivery_fee = item.get('delivery_fee')

    if radius is None or delivery_fee is None:
        print(f"⚠️ Pulo: item {idx} sem radius ou delivery_fee: {item}")
        continue

    try:
        radius = float(radius)
        delivery_fee = str(delivery_fee)
    except Exception as e:
        print(f"⚠️ Pulo: item {idx} erro de conversão: {e}")
        continue

    circle = create_circle(origin_point, radius)

    intersec = polygon.intersection(circle)

    if intersec.is_empty:
        print(f"Raio de {radius} km não cabe, pulando.")
        continue

    name_with_fee = f"{int(radius)}KM - {delivery_fee}"

    add_polygon_to_kml(name_with_fee, intersec, doc)
    print(f"✅ {name_with_fee} adicionado.")

tree = etree.ElementTree(kml_root)
tree.write("final_kml_com_fees.kml", pretty_print=True, xml_declaration=True, encoding="UTF-8")

print("✅ KML gerado: final_kml_com_fees.kml")
