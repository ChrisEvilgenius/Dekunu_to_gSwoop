# Dekunu_to_gSwoop

Batch converts all Dekunu GPS csv logs in specified directory to csv files 
formatted to be read by gSwoop.

You can access the raw Dekunu logs by connecting the device to your PC in USB mode.

You will need to change the default read & write directories which are set to:

  read_dir = 'C:/Users/jones.cs/Documents/Dekunu/In/'
  out_dir = 'C:/Users/jones.cs/Documents/Dekunu/Out/'

These folders need to already be present, this script will not create them!

Steps necessary for conversion are:

        - read csv file from read_dir
        - convert seperate GPS and GPScentisecond fields to ISO date format
        - unit converstions
        - calcuate the N & E velocity components from the compass heading & groundspeed
        - write output csv file to out_dir with gSwoop_' prefix
