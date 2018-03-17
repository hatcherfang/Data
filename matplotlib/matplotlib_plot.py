import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
year = [1950, 1970, 1990, 2010]
pop = [2.519, 3.692, 5.263, 6.972]
plt.plot(year, pop)
# x-axis
plt.xlabel('Year')
# y-axis
plt.ylabel('Population')
# title
plt.title('World Population Projections')
# y-axis ticks
# unit 'B' -> billion
plt.yticks([0, 2, 4, 6],
           ['0', '2B', '4B', '6B'])
plt.show()
plt.savefig("./plot.png")
