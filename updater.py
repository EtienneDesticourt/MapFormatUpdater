import json

POINT_FORMAT = "{{\"y\":{y},\"x\":{x}}}"
FACE_FORMAT = "{{\"v3\":{},\"v2\":{},\"v1\":{}}}"
MAP_FORMAT = "[{}]"


def parse_polygon(json_data):
    north = json_data['north']
    p1 = (north['east'], north['y'])
    p2 = (north['west'], north['y'])
    south = json_data['south']
    p3 = (south['west'], south['y'])
    p4 = (south['east'], south['y'])
    return [p1, p2, p3, p4]


def parse_connection(json_data):
    p1 = (json_data['east'], json_data['y'])
    p2 = (json_data['west'], json_data['y'])
    p3 = (json_data['south'], json_data['y'])
    p4 = (json_data['north'], json_data['y'])
    return [p1, p2, p3, p4]


def read_map(file_path):
    with open(file_path, "r") as f:
        data = f.read()
        trapezoids_data = json.loads(data)['trapezoids']
        connections_data = json.loads(data)['connections']

    trapezoids = [parse_polygon(trap) for trap in trapezoids_data]
    connections = [parse_connection(conn) for conn in connections_data]
    return trapezoids, connections


def polygon_to_faces(polygon):
    if len(polygon) != 4:
        raise ValueError("Polygon doesn't have 4 points.")

    face1 = polygon[:]
    # 2nd face is the 3 last points in the polygon (no matter the order, could
    # be 3 random points)
    face2 = polygon[1:]

    # We remove the point diagonally opposite to the point that's not in face2 from face1
    # This way they share two points and each have a diagonally opposed point
    x1, y1 = face1[0]
    for point in face2:
        x, y = point
        if x != x1 and y != y1:
            face1.remove(point)
            break

    #Uncomment if we care.
    #if len(face1) != 3 or len(face2) != 3:
    #    print(polygon)
    #    raise ValueError("Polygon isn't a trapezoid.")

    return face1, face2


def format_face(face):
    point_data = [POINT_FORMAT.format(x=point[0], y=point[1]) for point in face]
    face_data = FACE_FORMAT.format(*point_data)
    return face_data


def write_faces(faces, map_path):
    faces_data = [format_face(face) for face in faces]
    map_data = MAP_FORMAT.format(",".join(faces_data))

    with open(map_path, "w") as f:
        f.write(map_data)

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        input_map_path = sys.argv[1]
        output_map_path = sys.argv[2]
    else:
        print("Usage: python updater.py INPUT_MAP_PATH OUTPUT_MAP_PATH")
        sys.exit()

    print("Reading map:", input_map_path)
    traps, conns = read_map(input_map_path)

    print("Found", len(traps), "trapezoids.")
    print("Found", len(conns), "connections.")

    faces = [face for polygon in traps for face in polygon_to_faces(polygon)]

    print(faces[0])
    point = faces[0][0]
    f = POINT_FORMAT.format(x=point[0], y=point[1])
    print(f)
    f = format_face(faces[0])
    print(f)
    write_faces(faces, output_map_path)
