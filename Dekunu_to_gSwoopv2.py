"""
Created on Wed Apr 11 18:26:51 2018

Batch converts all Dekunu GPS csv logs in specified directory to csv files 
formatted to be read by gSwoop

@author: jones.cs
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import csv
import glob, os

# Define the path for both the source & output csv files
read_dir = 'C:/Users/jones.cs/Documents/Dekunu/In/'
out_dir = 'C:/Users/jones.cs/Documents/Dekunu/Out/'

# Create a list of all csv files in the read directory
extension = 'csv'
os.chdir(read_dir)
files = [i for i in glob.glob('*.{}'.format(extension))]

def convert(file_name, read_dir, out_dir):
    """Converts Dekunu csv logs to a valid gSwoop csv file via the following steps:
        - read csv file from read_dir
        - convert seperate GPS and GPScentisecond fields to ISO date format
        - unit converstions
        - calcuate the N & E velocity components from the compass heading & groundspeed
        - write output csv file to out_dir with gSwoop_' prefix"""

    file_path = read_dir+file_name
    df = pd.read_csv(file_path, header=0, sep=',')

    # Combine the gpsTime with centiseconds
    df['time'] = df['gpsTime'] + df['gpsTimeCentiSec']/100

    # time delta from epoch start @ 1970-01-01UTC + (elapsed time - (leap_count(2014) - leap_count(1980)))
    df['time'] = datetime(1970, 1, 1) + pd.to_timedelta(df['time'] - (35 - 19), unit='s')

    # Apply gSwoop time format e.g. 2016-09-10T14:20:51.40Z
    df['time'] = df['time'].dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    df['velD'] = df['instVertSpeedMetersPerSec'] * -1 # Down is positive
    df['groundspeed'] = df['gpsSpeedKnot'] * 0.514444 # Convert from knots to meters per second
    df['lat'] = df['gpsLatitude']/1e6 # lat needs six deimal places
    df['lon'] = df['gpsLongitude']/1e6 # Lon needs six deimal places

    # Calculate North & East velocity components
    conditions = [
        (df['gpsAngleDegree'] >= 0) & (df['gpsAngleDegree'] < 90),
        (df['gpsAngleDegree'] >= 90) & (df['gpsAngleDegree'] < 180),
        (df['gpsAngleDegree'] >= 180) & (df['gpsAngleDegree'] < 270),
        (df['gpsAngleDegree'] >= 270) & (df['gpsAngleDegree'] < 360)]

    velN_calc = [
        (  df['groundspeed'] * np.cos(np.radians(df['gpsAngleDegree']))),
        (- df['groundspeed'] * np.cos(np.radians(180 - df['gpsAngleDegree']))),
        (- df['groundspeed'] * np.cos(np.radians(df['gpsAngleDegree'] - 180))),
        (  df['groundspeed'] * np.cos(np.radians(360 - df['gpsAngleDegree'])))]

    velE_calc = [
        (  df['groundspeed'] * np.sin(np.radians(df['gpsAngleDegree']))),
        (  df['groundspeed'] * np.sin(np.radians(180 - df['gpsAngleDegree']))),
        (- df['groundspeed'] * np.sin(np.radians(df['gpsAngleDegree'] - 180))),
        (- df['groundspeed'] * np.sin(np.radians(360 - df['gpsAngleDegree'])))]

    df['velN'] = np.select(conditions, velN_calc)
    df['velE'] = np.select(conditions, velE_calc)
    
    # Fix column naming and create dummy data for missing columns
    df['heading'] = df['gpsAngleDegree']
    df['numSV'] = df['gpsNumOfSats']
    df['hMSL'] = df['altitudeAboveGroundMeters']
    df['hAcc'] = 1
    df['vAcc'] = 1
    df['sAcc'] = 1
    df['cAcc'] = 1
    df['gpsFix'] = 1

    headers1 = ['time','lat','lon','hMSL','velN','velE','velD','hAcc','vAcc','sAcc','heading','cAcc','gpsFix','numSV']
    headers2 = ['','(deg)','(deg)','(m)','(m/s)','(m/s)','(m/s)','(m)','(m)','(m/s)','(deg)','(deg)','','']

    out = df[headers1]
    out = out.groupby('time').mean().reset_index()
    out.loc[0] = headers2
    
    # Write results to csv, output file is source file name prefixed by 'out'
    file_path_out = out_dir+'gSwoop_'+file_name

    out.to_csv(path_or_buf=file_path_out, 
          sep=',', 
          mode='a',
          header = True, # This keeps the header in the csv file
          index= False)  # Index False removes the row numbers present in the Datatable
    
# Iterate through all csv files in read_dir and write series of converted files to out_dir
for file_name in files:

    convert(file_name, read_dir, out_dir)