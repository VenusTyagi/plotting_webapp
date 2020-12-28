import streamlit as st
import numpy as np
import pandas as pd
import json
# import altair as alt
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

    metrics= [1,2,3,4,5,6,7,9,10, "All moves together"]
    cols = st.selectbox('Select the move number to analyse plot',metrics )
    # st.write(f" The option to be selected is {cols}")
    moves = data['moves']

    if cols == 'All moves together':  
        StickPositions = combine_all('StickPositions', moves)
        RedDrumPositions = combine_all('RedDrumPositions', moves)
        bludrumposition = combine_all('BlueDrumPositions', moves)

    else:
        StickPositions = pd.DataFrame(moves[cols]['StickPositions'])
        RedDrumPositions = pd.DataFrame(moves[cols]['RedDrumPositions'])
        bludrumposition = pd.DataFrame(moves[cols]['BlueDrumPositions']) 


    bludrumposition['x'], bludrumposition['y'], bludrumposition['z'] = zip(*bludrumposition['position'].map(txtsplit))
    RedDrumPositions['x'], RedDrumPositions['y'], RedDrumPositions['z'] = zip(*RedDrumPositions['position'].map(txtsplit))
    StickPositions['x'], StickPositions['y'], StickPositions['z'] = zip(*StickPositions['position'].map(txtsplit))

    bludrumposition = clean_df(time_correction(bludrumposition.reset_index(drop=True)))
    RedDrumPositions = clean_df(time_correction(RedDrumPositions.reset_index(drop=True)))
    StickPositions = clean_df(time_correction(StickPositions.reset_index(drop=True)))
# --------------------------------------------------------------------------------------------------------------
    plots = st.selectbox("Which graph do you want to visualise", ['Distance Plot', '2d Plot', '3d Plot'])
    if plots == 'Distance Plot' :
        df_distance = pd.DataFrame(columns=['time','distance_BD_ST', 'distance_RD_ST', 'distance_RD_BD'])
        # asset = st.selectbox("Select the asset you want to see:",['StickPositions','RedDrumPositions','Bludrumposition'])
        for (_,p),(_,q),(_,r) in zip(StickPositions.iterrows(), bludrumposition.iterrows(), RedDrumPositions.iterrows()):
        #     print (p,q,r, sep= "\n--------------\n")
            df_distance.loc[_,'time'] = StickPositions.loc[_,'corr_time']
            df_distance.loc[_,'distance_BD_ST'] = distance(tuple(p.to_list()), tuple(q.to_list()))
            df_distance.loc[_,'distance_RD_ST'] = distance(tuple(p.to_list()), tuple(r.to_list()))
            df_distance.loc[_,'distance_RD_BD'] = distance(tuple(q.to_list()), tuple(r.to_list()))
        f,ax = plt.subplots(figsize=(18,4))
        ax.plot(df_distance['time'],df_distance['distance_BD_ST'])
        ax.plot(df_distance['time'],df_distance['distance_RD_ST'])
        ax.plot(df_distance['time'],df_distance['distance_RD_BD'])
        plt.legend(['BD & Sticks', 'RD & Sticks', 'BD & RD'])  
        plt.title('Distance betweem Assets')
        st.pyplot(f)
    

    

    # useraxis = st.multiselect("Select the axis you want to see the graph for :",['x','y','z'])
    # st.write(f" The plot will be between the axis - {useraxis}")
    # if len(useraxis) > 1:
    #     if line_plot == 'StickPositions' :
    #         st.line_chart(StickPositions[[useraxis[0],useraxis[1]]]) 
    #     if line_plot == 'RedDrumPositions' :
    #         st.line_chart(RedDrumPositions[[useraxis[0],useraxis[1]]]) 

    #     if line_plot == 'Bludrumposition' :
    #     #         st.line_chart(bludrumposition[['x','y']])
    #         st.line_chart(bludrumposition[[useraxis[0],useraxis[1]]]) 
    # elif len(useraxis) == 1 :
    #     st.write("Enter one more axis")

