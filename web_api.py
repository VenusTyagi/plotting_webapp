import streamlit as st
import numpy as np
import pandas as pd
import json
# import altair as alt
import matplotlib.animation as animation
import matplotlib.pyplot as plt
st.image('headerproject.jpg',width = 800)
# st.altair_chart
def txtsplit(x):
    return x.split(",")[0], x.split(",")[1], x.split(",")[2]

def distance(coord1, coord2):
    """
    the distance between two points
    """
    d = 0
    for i in range(1,4):
        d = d + (coord1[i] - coord2[i])**2
        
    d= d**0.5
    return d

def combine_all(asset, moves):
    """
    Combining all the moves together. 
    """
    df = pd.DataFrame()
    for i in range(len(moves)):
        temp = pd.DataFrame(moves[i][asset])
        df = df.append(temp)
    
    return df
    
def time_correction(df):
    """The first time will be the referrence point till the end of the move"""

    df['corr_time'] = df['time'].apply(lambda x : float(x)  - int(df.loc[0,'time'].split(".")[0]))

    return df

def clean_df(df):
    """remove the position and old time columns"""
    df.drop(labels = ['position', 'time'], axis=1, inplace=True) ##removes positiona nd time column
    df.sort_values(by=['corr_time'], inplace=True) ##sort the df w.r.t time
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype('float32')
    return df[[ 'corr_time','x', 'y', 'z']]



file1 = st.file_uploader('Upload JSON for Analysis')
if file1:
    data = json.load(file1)

    st.markdown('#### `Username` : ' + data['UserName'] )
    st.markdown('#### `Correctmoves`: ' + str(data['CorrectMoves']) )
    st.markdown('#### `Feedback` : ' + data['Feedback'] )

    st.markdown('-----------------------------------------------------------------------------------')
    st.markdown('### Select Moves')

    metrics= [1,2,3,4,5,6,7,9, "All moves together"] ### Find moves from the uploaded json as a next feature
    cols = st.selectbox('Select the move number to analyse plot',metrics )
    # st.write(f" The option to be selected is {cols}")
    moves = data['moves']

    if cols == 'All moves together':  
        StickPositions = combine_all('StickPositions', moves)
        RedDrumPositions = combine_all('RedDrumPositions', moves)
        BlueDrumPositions = combine_all('BlueDrumPositions', moves)

    else:
        StickPositions = pd.DataFrame(moves[cols]['StickPositions'])
        RedDrumPositions = pd.DataFrame(moves[cols]['RedDrumPositions'])
        BlueDrumPositions = pd.DataFrame(moves[cols]['BlueDrumPositions']) 


    BlueDrumPositions['x'], BlueDrumPositions['y'], BlueDrumPositions['z'] = zip(*BlueDrumPositions['position'].map(txtsplit))
    RedDrumPositions['x'], RedDrumPositions['y'], RedDrumPositions['z'] = zip(*RedDrumPositions['position'].map(txtsplit))
    StickPositions['x'], StickPositions['y'], StickPositions['z'] = zip(*StickPositions['position'].map(txtsplit))

    BlueDrumPositions = clean_df(time_correction(BlueDrumPositions.reset_index(drop=True)))
    RedDrumPositions = clean_df(time_correction(RedDrumPositions.reset_index(drop=True)))
    StickPositions = clean_df(time_correction(StickPositions.reset_index(drop=True)))
# ------------------------------- Plot---------------------------------------------------------------------
    plots = st.selectbox("Which graph do you want to visualise", ['Distance Plot', '2d Plot', '3D Heatmap'])
# ------------------------------- Distance ---------------------------------
    if plots == 'Distance Plot' :
        df_distance = pd.DataFrame(columns=['time','distance_BD_ST', 'distance_RD_ST', 'distance_RD_BD'])
        # asset = st.selectbox("Select the asset you want to see:",['StickPositions','RedDrumPositions','BlueDrumPositions'])
        for (_,p),(_,q),(_,r) in zip(StickPositions.iterrows(), BlueDrumPositions.iterrows(), RedDrumPositions.iterrows()):
        #     print (p,q,r, sep= "\n--------------\n")
            df_distance.loc[_,'time'] = StickPositions.loc[_,'corr_time']
            df_distance.loc[_,'distance_BD_ST'] = distance(tuple(p.to_list()), tuple(q.to_list()))
            df_distance.loc[_,'distance_RD_ST'] = distance(tuple(p.to_list()), tuple(r.to_list()))
            df_distance.loc[_,'distance_RD_BD'] = distance(tuple(q.to_list()), tuple(r.to_list()))
        fig,ax = plt.subplots(figsize=(18,4))
        ax.plot(df_distance['time'],df_distance['distance_BD_ST'])
        ax.plot(df_distance['time'],df_distance['distance_RD_ST'])
        ax.plot(df_distance['time'],df_distance['distance_RD_BD'])
        ax.set_xlabel(f'Time' )
        ax.set_ylabel(f'Distance between two assets' )
        plt.legend(['BD & Sticks', 'RD & Sticks', 'BD & RD'])  
        plt.title('Distance betweem Assets')
        st.pyplot(fig)
# ------------------------------- 3d ---------------------------------
    if plots == '3D Heatmap' : 
        asset = st.selectbox("Select the asset:",['Stick','RedDrum','BlueDrum'])
        fig = plt.figure(figsize=(10,10))
        ax = plt.subplot(111, projection='3d')
        # ax.xaxis.pane.fill = False
        # ax.xaxis.pane.set_edgecolor('white')
        # ax.yaxis.pane.fill = False
        # ax.yaxis.pane.set_edgecolor('white')
        # ax.zaxis.pane.fill = False
        # ax.zaxis.pane.set_edgecolor('white')
        # ax.grid(False)
        
        # Remove z-axis
        ax.w_zaxis.line.set_lw(0.)
        ax.set_zticks([])
        xyz = StickPositions.iloc[:,1:].to_numpy()
        red = RedDrumPositions.iloc[:,1:].to_numpy()
        blue = BlueDrumPositions.iloc[:,1:].to_numpy() 

        ax.scatter(xyz[:,0], xyz[:,1], xyz[:,2],c='black' ,s=4)
        ax.scatter(blue[:,0], blue[:,1], blue[:,2],c='b' ,s=4)
        ax.scatter(red[:,0], red[:,1], red[:,2], c='r',s=4)

        ax.set_xlabel(f'x position of Sticks' )
        ax.set_ylabel(f'y position of Sticks' )
        st.pyplot(fig)
