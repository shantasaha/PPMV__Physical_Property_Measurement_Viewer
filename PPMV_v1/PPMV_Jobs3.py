##PPMV Jobs now with Pandas to make it easier
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
from random import randint
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)


################################################################################
##################################Base Functions################################
################################################################################

#Functions that assist with basic tasks, such as grabbing data from machines,
#basic plotting, fitting, and calculation. These functions are combined to form
#the user friendly "Jobs" functions

def Read_PPMS_File(DAT_name,MachineType):
    #Function reads in file and returns needed parameters based on the machine
    #used and the bridges used
    #make sure to keep header for pandas usage
   
   if MachineType==('9T-ACT' or '14t-ACT'):
       headerskip=25
        #Pull coulums: [Temp (K),Field(Ore), Sample Orientation (deg angle)]
       cols=[3,4,5]
   elif MachineType==('9T-R' or '14T-R'): 
        headerskip=31
        cols=[3,4,5]
   elif MachineType=='Dynacool':
        headerskip=30
        cols=[3,4,5]
   else:
        NameError('Please specify MachineType as 9T, 14T, or Dynacool or _ACT varient')
    

    ##specify which birdges to extract for Linear Resistivity
   if MachineType==('9T-ACT' or '14t-ACT'):
       cols=cols+[12,13]
       
   else:
       cols=cols+[19,20,21]
        
   #Now load in the file and return as a Pandas data frame. 
   #The order of data is [Temp (K),Field(Ore), Sample Orientation (deg angle), R (first birdge given), R (second bridge given), etc)
   data=pd.read_csv(DAT_name,skiprows=headerskip,usecols=cols)
   
   #rename columns so that it is universal
   if MachineType==('9T-ACT' or '14t-ACT'):
       #skip bridge 3 for ACT pucks
       data.columns=['Temperature (K)','Field (Oe)', 'theta (deg)', 'Bridge1_R (ohms)','Bridge2_R (ohms)']
   else:
       data.columns=['Temperature (K)','Field (Oe)', 'theta (deg)', 'Bridge1_R (ohms)','Bridge2_R (ohms)','Bridge3_R (ohms)']
       
   #fill all NaNs with zeros
   data.fillna(0, inplace=True)
   return data

def Fill_Data(data):
    #fills in the missing bridges with zeros for your data file
    
    #Fill data with zeros at the end to make full size
    FillLength=data.shape[0]
    FillZeros=np.zeros((FillLength,1))
    
    while data.shape[1]<7:
        #add on column of zeros
        Newdata=np.hstack((data,FillZeros))
        data=Newdata
        
    return data


def Split_Sets_Index_Reversed(x_data,SplitVal,Reversal):
    #Finds index where a parameter is reversed (say between a cool down and warm up)
    xsize=len(x_data)
    for i in range(xsize):
        #find where index has been reversed. either 'down to up' or 'up to down'
        difference=x_data[i+1]-x_data[i]
        #print(difference)
        if Reversal=='down to up':
            if difference>SplitVal:
                CutIndex=i
                print(CutIndex)
                break
        else:
            if difference<SplitVal:
                CutIndex=i
                break
            
    return CutIndex

################################################################################
#############################Pre-Select Jobs####################################
################################################################################



def Job_QuickPlot(DAT_name,MachineType,Xaxis,Yaxis):
    #Quick Plot function for Quick Plot button
    #First, load data
    #We need which bridge to grab for bridge numbers, if selected
 
  
    
    #read in data as a pandas dataframe    
    data=Read_PPMS_File(DAT_name,MachineType)
   
    
    #grab needed data for x and y axis using Xaxis name to get the column and name the axis
    
    Xdata=data[Xaxis]
    Xname=Xaxis
        
    Ydata=data[Yaxis]
    Yname=Yaxis
    
   
    plt.figure()
    plt.plot(Xdata,Ydata,'-')
    plt.xlabel(Xname,fontsize=12)
    plt.ylabel(Yname,fontsize=12)
    plt.title('')
    plt.tight_layout()
    plt.show()
    

def Job_CWPlot(X1=np.NaN,Y1=np.NaN,X2=np.NaN,Y2=np.NaN,empty=False):
    #test data
    
    #returns figures and axes needed for CW plot
    #generate figure 
    fig=Figure()
    
    #create subplot to plot inside of
    CWPlot=fig.add_subplot(1,1,1)
    #return empty plot if specified to
    checkdata=np.array([X2,Y2])
    print(type(checkdata))
    if empty:
        CWPlot.plot(np.NaN,np.NaN)
    #if one of the lines is empty, give only one plot
    elif pd.isnull(checkdata).all():
        print('only have one plot')
        CWPlot.plot(X1,Y1)
    else:
        CWPlot.plot(X1,Y1,'b',label='cool down')
        CWPlot.plot(X2,Y2,'r',label='warm up')
        CWPlot.legend(loc='best')
        
    #Adjust Plot Settings
    CWPlot.tick_params(direction='in')
    
    
    return fig,CWPlot


def Job_CW_Split_Data(Xdata,Ydata): 
    data=np.transpose([Xdata,Ydata])
    print('shape of data is')
    print(np.shape(data))
    
    SplitVals=0.1
    
    #Find index of split
    Index=Split_Sets_Index_Reversed(Xdata,SplitVals,'down to up')
    print('on split '+str(1))
    print(Index)
    
    #split the whole set and save split, (save last one if you are on the last cycle)
    data2=data[(Index+1):,:]
    data1=data[0:(Index+1),:]
    #saves new data for next cycle
    data=data2
    
    print('data1 temp')
    print(data1[0:5,0])
    print('data2 temp')
    print(data2[0:5,0])
    
    print('data1 shape is')
    print(np.shape(data1))
    
    X1,Y1=data1[:,0],data1[:,1]
    X2,Y2=data2[:,0],data2[:,1]
    
    return X1,Y1,X2,Y2
    
    
    