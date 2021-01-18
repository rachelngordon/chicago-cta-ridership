import numpy as np
import pandas as pd
import csv

# read in the files
ridership=pd.read_csv('CTA_L_Ridership.csv')
system_data=pd.read_csv('CTA_L_System_Data.csv')

# What is the annual ridership for the Loyola stop for the available data?
# creates a series for ridership at the Loyola stop
loyola=ridership[ridership.stationname.isin(['Loyola'])]

# function for calculating annual ridership for the Loyola stop
def yearly_ridership(year):
    startdate='01/01/'+year

    # creates a series of days in the given year and then creates a series for ridership at Loyola during that year
    year_dates=pd.date_range(startdate, periods=365, freq='D')
    year_dates=year_dates.strftime('%m/%d/%Y')
    loyola_year=loyola[loyola.date.isin(year_dates)]
    
    # calculates total rides during that year at Loyola
    annual_rides=loyola_year['rides'].sum()
    annual_rides=str(annual_rides)
    return annual_rides

# creates a list of years 2001 through 2020 and maps each item in the list to a string
# also does the same thing for the last four years excluding 2020 in the list of years (2016-2019) for Question 3
years=list(range(2001,2021))
five_years=years[15:20]
years=map(str,years)

# writes the year and annual ridership for that year to a csv file by calling the yearly_ridership fucntion
g=open('annual_ridership_Loyola1.csv','w')

with g:
    writer=csv.writer(g)
    writer.writerow(['Year', '# Station Entries'])
    for year in years:
        writer.writerow([year,yearly_ridership(year)])

g.close()

# Can you guess from CTA ridership when Loyola closed last spring for COVID?

# creates a range of dates from February to March and creates a series for ridership at Loyola during February and March
feb_mar=pd.date_range('02/01/2020','03/30/2020',freq='D')
feb_mar=feb_mar.strftime('%m/%d/%Y')
loyola_fm=loyola[loyola.date.isin(feb_mar)]

# write the date and number of station entries at Loyola to a csv file for the dates in February and March 2020
loyola_fm.to_csv('annual_ridership_Loyola2.csv', index=False, columns=['date','rides'], header=['Day','# Station Entries'])

# Loyola probably closed around 03/20/2020 because the day after March 30 CTA ridership dropped significantly to below 1000, much lower than it had been previously during those months
# appends the estimated day Loyola closed to the csv file
g=open('annual_ridership_Loyola2.csv','a')
g.write('Estimated Day Loyola closed: 03/20/2020')
g.close()

# What has been the impact of COVID on CTA ridership?
# Calculate the monthly ridership for each of the CTA lines for the last 5 years

# creates a new dataframe by merging the two csvs for CTA ridership and system data based on the map/station id
full_data=pd.merge(ridership, system_data, left_on='station_id', right_on='MAP_ID')

# function for finding the monthly ridership based on the first day of the month and its number of days
def monthly_ridership(startdate,num_days):
    month_dates=pd.date_range(startdate, periods=num_days, freq='D')
    month_dates=month_dates.strftime('%m/%d/%Y')
    # creates a new dataframe for data from the given month and returns that data frame
    monthly_ridership=full_data[full_data.date.isin(month_dates)]
    return monthly_ridership

# lists of number of days in each month, and a list for only the first six months which will be used to calculate ridership for 2020
month_days={'01':31, '02':28, '03':31, '04':30, '05':31, '06':30, '07':31, '08':31, '09':30, '10':31, '11':30, '12':31}
six_months={'01':31, '02':28, '03':31, '04':30, '05':31, '06':30}

# function for finding the total ridership for each line of the CTA in a given year
def line_ridership(line, year):
    line_ridership={}
    for month in month_days:
        # calculates the sum of station entries for each line during each month in the given year
        month_ridership=monthly_ridership(month+'/01/'+year,month_days[month])
        month_sums=month_ridership.groupby(line).sum()
        line_ridership[month+'/'+year]=month_sums['rides'][True]
    return line_ridership

# list of lines on the CTA (as written in the system data for the sake of referencing the file)
lines=['RED', 'BLUE', 'G', 'BRN', 'P', 'Pexp', 'Y', 'Pnk', 'O']

# Calulate the increase/decrease of ridership for each year relative to the prior year
annual_ridership=[]

# calculates annual ridership for each year
years_list=list(range(2001,2021))

for year in years_list:
    annual_ridership.append(yearly_ridership(str(year)))

# function for calulcating the increase/decrease in ridership from the previous year based on the list of annual ridership
def yearly_change(year_index):
    inc_dec=int(annual_ridership[year_index])-int(annual_ridership[year_index-1])
    return inc_dec

# begin writing data to monthly ridership csv file
g=open('monthly_ridership.csv','w')

with g:
    writer=csv.writer(g)
    # function for writing each month from the dictionary returned by the line ridership function to a file
    def write_dict(months_dict):
        for month in months_dict:
            writer.writerow([month, months_dict[month]])
    # writes the name of each line, column labels, and monthly ridership for the last five years to a file by looping through the list of CTA lines
    for line in lines:
        writer.writerow(['Line: '+line])
        writer.writerow(['Month', '# Station Entries'])
        write_dict(line_ridership(line, '2016'))
        write_dict(line_ridership(line, '2017'))
        write_dict(line_ridership(line, '2018'))
        write_dict(line_ridership(line, '2019'))
        # loop for calculating ridership for the given line during the first six months of 2020 and writing it to the file
        x={}
        for month in six_months:
            month_ridership=monthly_ridership(month+'/01/2020',six_months[month])
            month_sums=month_ridership.groupby(line).sum()
            x[month+'/2020']=month_sums['rides'][True]
        write_dict(x)
    # writes yearly increase/decrease in ridership to the file by looping through the indices in the list of annual ridership
    writer.writerow(['Year', 'Increase/Decrease from previous year'])
    for i in range(1, len(annual_ridership)):
        x=yearly_change(i)
        # includes the sign (+/-) before the number based on if it is an increase or decrease in ridership
        if x > 0:
            writer.writerow([str(years_list[i]), '+'+str(x)])
        else:
            writer.writerow([str(years_list[i]), str(x)])

g.close()

# Relative to 1/1/2019-6/30/2019, how much more/less money has the CTA made during the first 6 months of 2020?
# function that returns the total number of rides on the CTA during the first six months of a given year
def sixmo_ridership(year):
    # creates start and end dates based on the year given
    startdate='01/01/'+year
    enddate='06/30'+year

    # creates a range of dates for the first six months of a year
    year_dates=pd.date_range(startdate, periods=182, freq='D')
    year_dates=year_dates.strftime('%m/%d/%Y')

    # creats a series for ridership during these six months and calculates the total number of rides in this time period
    sixmo_ridership=ridership[ridership.date.isin(year_dates)]
    total_rides=sixmo_ridership['rides'].sum()
    return total_rides

# creates variables for total rides during the first six months of 2019 and 2020
ridership19=sixmo_ridership('2019')
ridership20=sixmo_ridership('2020')

# calculates the revenue earned by the CTA during the first six months of 2019 and 2020 and formats it to contain two decimal places
revenue19=ridership19*2.50
revenue19="{:.2f}".format(revenue19)

revenue20=ridership20*2.50
revenue20="{:.2f}".format(revenue20)

# writes the results to a file
g=open('ridership_revenue.csv','w')

with g:
    writer=csv.writer(g)
    writer.writerow(['Date Range', '# Station Entries', 'Revenue'])
    writer.writerow(['01/01/2019-06/30/2019',ridership19, '$'+str(revenue19)])
    writer.writerow(['01/01/2020-06/30/2020',ridership20, '$'+str(revenue20)])

g.close()
