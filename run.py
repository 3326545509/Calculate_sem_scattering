import json
from datetime import datetime
import os 
import sys
import numpy as np

def grandsonfunction_set_homo(nx,ny):
    vpvsRatio           =   main_config['VpvsRatio']
    backGroundVelocity  =   main_config['BackGroundVelocity']

    #给定材料，即速度结构
    with open('semcode/DATA/nbmodels.txt','w')as f:
        f.write('nbmodels = 1\n')
        f.write('1 1 2700.d0 ' + str(vpvsRatio*backGroundVelocity) + ' ' + str(backGroundVelocity) + ' 0 0 9999 9999 0 0 0 0 0 0\n')
        f.close()
    os.system("cd semcode/DATA;sed -i '/position_insert_nbmodels/ r nbmodels.txt' Par_file")

    #根据所给的材料设置网格的位置，即给每一块区域填上速度结构
    with open('semcode/DATA/nbregions.txt','w')as f:
        f.write('nbregions = 1\n')
        f.write('1 '+str(nx)+' 1 '+str(ny)+' 1\n')
        f.close()
    os.system("cd semcode/DATA;sed -i '/position_insert_nbregions/ r nbregions.txt' Par_file")

    print('homo is set')

def grandsonfunction_set_pert(nx,ny):
    vpvsRatio           =   main_config['VpvsRatio']
    backGroundVelocity  =   main_config['BackGroundVelocity']
    scatters    =   main_config['Scatters']

    models      =   []
    for scatter in scatters:
        sigma   =   scatter['Diameter']/2 #sigma是高斯体的半径
        mux    =   scatter['Position']['X']
        muy    =   scatter['Position']['Y']
        dx              =   main_config['Dx']
        dvPercent   =   scatter['DvPercent']

        for i in range(-int(sigma/dx)-20,int(sigma/dx)+20):
            for j in range(-int(sigma/dx)-20,int(sigma/dx)+20):
                x   =   i * dx 
                y   =   j * dx 
                if (x**2+y**2)>sigma**2:
                    continue
                if scatter['Style'] ==  'Gauss':
                    velo    =    dvPercent*backGroundVelocity*np.exp(  -(x**2+y**2)/(2*sigma**2)  )+backGroundVelocity
                elif scatter['Style'] == 'Circle':
                    velo    =       backGroundVelocity*(1+dvPercent)
                else:
                    print('Error! scatter style not defined!')
                    sys.exit()
                models.append([i+int(mux/dx),j+int(muy/dx),velo])
    
    length  =   len(models)+1
    #给定材料，即速度结构
    with open('semcode/DATA/nbmodels.txt','w')as f:
        f.write('nbmodels = '+str(length)+'\n')
        f.write('1 1 2700.d0 ' + str(vpvsRatio*backGroundVelocity) + ' ' + str(backGroundVelocity) + ' 0 0 9999 9999 0 0 0 0 0 0\n')
        for i in range(len(models)):
            index   =   str(i+2)
            v       =   models[i][2]
            f.write(index+' 1 2700.d0 ' + str(vpvsRatio*v) + ' ' + str(v) + ' 0 0 9999 9999 0 0 0 0 0 0\n')
        f.close()
    os.system("cd semcode/DATA;sed -i '/position_insert_nbmodels/ r nbmodels.txt' Par_file")

    with open('semcode/DATA/nbregions.txt','w')as f:
        f.write('nbregions = '+str(length)+'\n')
        f.write('1 '+str(nx)+' 1 '+str(ny)+' 1\n')
        for i in range(len(models)):
            index   =   str(i+2)
            nxstart =   models[i][0]
            nystart =   models[i][1]
            f.write(str(nxstart)+' '+str(nxstart+1)+' '+str(nystart)+' '+str(nystart+1)+' '+index+'\n')
        f.close()
    os.system("cd semcode/DATA;sed -i '/position_insert_nbregions/ r nbregions.txt' Par_file")


    print('pert is set')

def childfuncion_set_areaAndMaterial(homoOrPert,nx,ny):
    if homoOrPert   ==  'homo':
        grandsonfunction_set_homo(nx,ny)

    elif homoOrPert ==  'pert':
        grandsonfunction_set_pert(nx,ny)
    else:
        print('Error! homoOrPert is not defined')
        sys.exit()
    print('model and material are set')

def childfuncion_set_areaDtDx():
    timePropagate       =   main_config['TimePropagate']
    box_x               =   main_config['Box']['Length']
    box_y               =   main_config['Box']['Height']
    dx                  =   main_config['Dx']
    dt                  =   main_config['Dt']
    backGroundVelocity  =   main_config['BackGroundVelocity']
    freq                =   main_config['Source']['Freq']

    if dx/dt<backGroundVelocity:
        print('Error! dx/dt<c! not stable')
        sys.exit()
    
    if timePropagate    ==  'Default':
        timePropagate   =   max([box_x,box_y])/backGroundVelocity+1/freq
    else:
        timePropagate   =   timePropagate
    
    os.system("sed -i '/DT/s/=.*/="+str(dt)+"/g' ./semcode/DATA/Par_file")

    nstep   =   round(timePropagate   /   dt/100)*100
    os.system("sed -i '/NSTEP/s/=.*/="+str(nstep)+"/g' ./semcode/DATA/Par_file")

    xmax    =   round(box_x)
    nx      =   int(box_x/dx)+1
    os.system("sed -i '/xmax/s/=.*/="+str(xmax)+"/g' ./semcode/DATA/Par_file")
    os.system("sed -i '/nx/s/=.*/="+str(nx)+"/g' ./semcode/DATA/Par_file")


    ny      =   int(box_y/dx)+1
    with open('./semcode/DATA/interfaces_simple_topo_flat.dat','w')as f:
        f.write('2\n')
        
        f.write('2\n')
        f.write('0 0\n')
        f.write(str(box_x)+' 0\n')
        
        f.write('2\n')
        f.write('0 '+str(box_y)+'\n')
        f.write(str(box_x)+' '+str(box_y)+'\n')

        f.write(str(ny))
        
    print('set Dt,Dx,nstep,interfaces_simple_topo_flat.dat')
    return nx,ny

#写好了 01-07T22:55
def childfunction_stationfile_generate():
    position    =   np.loadtxt('addition_stationfile')
    if np.shape(position)   ==  (2,):#即只有一个台站的时候
        position    =   [position]
    newfile     =   []
    for i in range(len(position)):
        stationId='S'+str(i+1).zfill(4)
        newfile.append(stationId+' AA '+str(position[i][0])+' '+str(position[i][1])+' 0 0 ')
        
    with open('./semcode/DATA/STATIONS','w')as f:
        f.write("\n".join(newfile))
        f.close()
    
    print('staion file is generated')
    return

#写好了01-08T15:38
def set_parfile(homoOrPert):
    nx,ny   =   childfuncion_set_areaDtDx()
    childfuncion_set_areaAndMaterial(homoOrPert,nx,ny)
    print('OK. set_parfile done')
    

#写好了01-07T22：29
def set_source():
    source      =   main_config['Source']
    source_type        =   source['Type']
    position_x  =   source['Position']['X']
    position_y  =   source['Position']['Y']
    freq        =   source['Freq']
    
    if source_type=='SH':
        os.system("sed -i '/P_SV/s/=.*/="+".false."+"/g' ./semcode/DATA/Par_file")
    elif source_type=='P-SV':
        os.system("sed -i '/P_SV/s/=.*/="+".true."+"/g' ./semcode/DATA/Par_file")
    else:
        print('Error exist ! source type not defined well.')
        sys.exit()
    os.system("sed -i '/xs/s/=.*/="+str(position_x)+"/g' ./semcode/DATA/SOURCE")
    os.system("sed -i '/zs/s/=.*/="+str(position_y)+"/g' ./semcode/DATA/SOURCE")
    os.system("sed -i '/f0/s/=.*/="+str(freq)+"/g' ./semcode/DATA/SOURCE")
    
    print('OK. set_source done')
    return 

#写好了01-07T22:56
def set_station():
    station         =   main_config['Stations']
    station_type    =   station['Style']

    if station_type ==  'station_file_addition':
        #使用提前准备的台站，设成true
        os.system("sed -i '/use_existing_STATIONS/s/=.*/="+'.true.'+"/g' ./semcode/DATA/Par_file")
        childfunction_stationfile_generate()
    
    elif station_type=='station_parameterjson':
        os.system("sed -i '/use_existing_STATIONS/s/=.*/="+'.true.'+"/g' ./semcode/DATA/Par_file")
        #具体还没写完！
        print("Error!Not defined Here!")
        sys.exit()
    
    elif station_type=='station_parfile_with_hand':
        os.system("sed -i '/use_existing_STATIONS/s/=.*/="+'.false.'+"/g' ./semcode/DATA/Par_file")
        #具体还没写完！
        print("Error!Not defined Here!")
        sys.exit()
    
    else:
        print('Error! set_station parameter defined wrong!')
        sys.exit()
    
    print('OK. set_station done')
    return

def run_sem():
    os.system('cd semcode;./run_this_example.sh')
    print('OK. run_sem done')

#把所有用到的参数文件copy进结果文件夹，结果文件夹可以用时间戳来加标签，这样能防止重复
def analyse_result(timenow,outfile_to_analyse):
    if outfile_to_analyse   ==  'homo':
        os.system('cp parameter.json semcode/OUTPUT_FILES/')
        os.system('cd semcode;./ascii2sac OUTPUT_FILES/')
        os.system('mv semcode/DATA semcode/OUTPUT_FILES')
        os.system('mv semcode/OUTPUT_FILES semcode/OUTPUT_FILES_homo')

    elif outfile_to_analyse ==  'pert':
        os.system('cp parameter.json semcode/OUTPUT_FILES/')
        os.system('cd semcode;./ascii2sac OUTPUT_FILES/')
        os.system('mv semcode/DATA semcode/OUTPUT_FILES')
        os.system('mv semcode/OUTPUT_FILES semcode/OUTPUT_FILES_pert')

    elif outfile_to_analyse ==  'all_done':
        os.system('mkdir '+'OUTPUT/'+timenow)
        os.system('mv semcode/OUTPUT_FILES* OUTPUT/'+timenow)
        os.system('cp addition_stationfile OUTPUT/'+timenow)

    else:
        print('Error! outfile_to_analyse is not defined!')
        sys.exit()

    print('OK. analyse_result done')

if __name__=='__main__':

    time_run_this_code  =   datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    with open('parameter.json') as f:
        main_config  =   json.load(f)

    stateForCalculateion    =   ['homo']#['pert']    #['pert','homo']

    #只有在为了得到介质图像的时候这段if才有用
    if main_config['OnlyGetAScatterPicture']    ==  "True":
        main_config['TimePropagate']    =   5
        main_config['Source']['Type']   =   "P-SV"
        stateForCalculateion            =   ['pert']

    for homoPert in stateForCalculateion:
        os.system('rm -r semcode/DATA')
        os.system('cp -r DATA_origin semcode/DATA')
        set_source()
        set_station()
        set_parfile(homoOrPert = homoPert)
        run_sem()
        analyse_result(timenow=time_run_this_code,outfile_to_analyse=homoPert)
    analyse_result(timenow=time_run_this_code,outfile_to_analyse='all_done')