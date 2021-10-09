import math 

x = 50
y = 50

opposite_angle = round(math.degrees(math.asin(x/(x**2+y**2)**0.5)),2)

z = x/(x**2+y**2)**0.5
print(z)
a = math.asin(z)
print(a)
print(round(math.degrees(a),2))
