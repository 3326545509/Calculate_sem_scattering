import numpy as np 

#异常体的位置
xa  =   750e3
ya  =   750e3

#台站距离异常体的距离
l   =   100e3

with open('addition_stationfile','w')as f:
    for theta in np.linspace(0,np.pi/2-0.05,40):
        x1  =   l*np.cos(theta) + xa
        y1  =   l*np.sin(theta) + ya
        f.write(str(x1)+' '+str(y1)+'\n')
    for theta in np.linspace(np.pi/2,np.pi,10):
        x1  =   l*np.cos(theta) + xa
        y1  =   l*np.sin(theta) + ya
        f.write(str(x1)+' '+str(y1)+'\n')
    f.close()