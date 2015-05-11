import random

output = open('randomdata.txt', 'wb')
result = []

for i in range(0,1000):
	ttnum = 0
	for j in range(0, 350):
		randnum = random.random()
		output.write(str(randnum)+',')
		ttnum += randnum
	re = random.randrange(0,4)
	output.write(str(re)+'\n')
	#print 0 in result
	if not re in result:
		result.append(re)


print result
output.close()