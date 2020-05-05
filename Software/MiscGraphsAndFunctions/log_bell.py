"""

      .o.       ooooooooo.         .o.       oooooo     oooo 
     .888.      `888   `Y88.      .888.       `888.     .8'  
    .8"888.      888   .d88'     .8"888.       `888.   .8'   
   .8' `888.     888ooo88P'     .8' `888.       `888. .8'    
  .88ooo8888.    888`88b.      .88ooo8888.       `888.8'     
 .8'     `888.   888  `88b.   .8'     `888.       `888'      
o88o     o8888o o888o  o888o o88o     o8888o       `8'       
                                                             
File:     log_bell
Purpose:  Create a logarithmic horn in a 3D graph for use in diagrams/presentations
Creator:  Alexander McGinnis
Modifier: Joseph Haun
Updated:  5-5-2020

"""

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

fig = plt.figure()
#plt.axis('off')
ax = fig.gca(projection='3d')
#ax.set_axis_off()
#X, Y, Z = axes3d.get_test_data(0.05)


x = y = np.arange(1, 2, 0.006)
X, Y = np.meshgrid(x, y)

#Z = 1*np.log(1*(np.power(X,2)/2+np.power(Y,2)/2))
Z = 50*np.log(1*(np.power((X-1.5)/2,2)+np.power((Y-1.5)/2,2)))



X = X * 10
Y = Y * 10
Z = Z * 10

#ax.plot_surface(X, Y, Z, rstride=4, cstride=4, alpha=1,linewidth=0.5, antialiased=True,cmap=cm.coolwarm)
ax.plot_surface(X, Y, Z)
#cset = ax.contour(X, Y, Z, zdir='z', offset=-100, cmap=cm.coolwarm)
#cset = ax.contour(X, Y, Z, zdir='x', offset=-40, cmap=cm.coolwarm)
#cset = ax.contour(X, Y, Z, zdir='y', offset=40, cmap=cm.coolwarm)

ax.set_xlabel('X')
#ax.set_xlim(-40, 40)
ax.set_ylabel('Y')
#ax.set_ylim(-40, 40)
ax.set_zlabel('Z')
#ax.set_zlim(-40, 40)
ticks = np.around(np.linspace(0, 260, 10),0)
zticks = np.around(np.linspace(0, 4, 10),2)
print(zticks)
#ax.axes.xaxis.set_ticklabels([])
ax.axes.xaxis.set_ticklabels([])
ax.axes.yaxis.set_ticklabels([])
ax.axes.zaxis.set_ticklabels([])


#ax.set_axis_off()
plt.show()
