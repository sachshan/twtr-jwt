def calculate_centroid(points):
    latitudes = []
    longitudes = []

    for point in points:
        latitudes.append(point['location'][0])
        longitudes.append(point['location'][1])
    
    return [sum(latitudes) / len(latitudes), sum(longitudes) / len(longitudes)]


# points = [
#     {
#         "location": [
#             42.34571451749969,
#             -71.06247514486313
#         ],
#         "user_name": "Andrea"
#     },
#     {
#         "location": [
#             42.3536431252861,
#             -71.07771009206772
#         ],
#         "user_name": "Surabhi"
#     },
#     {
#         "location": [
#             42.33806979848312,
#             -71.08753234148026
#         ],
#         "user_name": "Shanu"
#     }
# ]

# print(calculate_centroid(points))