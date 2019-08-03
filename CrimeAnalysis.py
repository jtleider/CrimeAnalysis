import random
import pandas as pd
import matplotlib.pyplot as plt

def hourampm(date):
	hour = date.hour
	if hour // 12 == 0: ampm = 'AM'
	else: ampm = 'PM'
	hour12 = hour % 12
	if hour12 == 0: hour12 = hour12 + 12
	return '{}{}'.format(hour12, ampm)

readrows = None # number of rows of data to read in

crimes = pd.read_csv('Crimes_-_2001_to_present.csv', nrows=readrows)
print(crimes.shape)
print(crimes.dtypes)
crimes = crimes[['Date', 'IUCR', 'Primary Type', 'Description', 'Domestic', 'FBI Code', 'Year']]

################################################################################
########################## INITIAL DATA PROCESSING #############################
################################################################################
print(crimes.dtypes)
# Date
crimes['Date_str'] = crimes['Date']
crimes['Date'] = pd.to_datetime(crimes['Date'])
print(crimes[['Date_str', 'Date']].iloc[random.sample(range(len(crimes)), 50)])
del crimes['Date_str']
assert (crimes['Date'].transform(lambda date: date.year) == crimes['Year']).all()
del crimes['Year']
# IUCR codes
codes = crimes[['IUCR', 'Primary Type', 'Description']].drop_duplicates()
print(codes.groupby('IUCR').filter(lambda g: g.shape[0] != 1)) # IUCR matches specific 'Primary Type' and 'Description', with minor exceptions
assert (codes.groupby(['Primary Type', 'Description']).size() == 1).all() # 'Primary Type' and 'Description' match to a single IUCR code
for code in codes.columns:
	assert not codes[code].isnull().any()
print(crimes[['IUCR', 'Domestic']].drop_duplicates().sort_values(['IUCR', 'Domestic']).head()) # 'Domestic' varies within IUCR codes
# FBI codes
# IUCR codes and FBI codes are measured differently; they do not nest in either direction
fbicodes = crimes[['IUCR', 'Primary Type', 'Description', 'FBI Code']].drop_duplicates()
print(fbicodes.groupby('FBI Code').filter(lambda g: g.shape[0] > 1).sort_values('FBI Code').head(30)) 
print(fbicodes.groupby('IUCR').filter(lambda g: g.shape[0] > 1).sort_values('IUCR').head(30)) 

################################################################################
######################## CREATE ANALYTICAL VARIABLES ###########################
################################################################################
crimes['violent'] = crimes['FBI Code'].isin(['01A', '02', '03', '04A', '04B']) # based on http://gis.chicagopolice.org/clearmap_crime_sums/crime_types.html
print(crimes[['IUCR', 'Primary Type', 'FBI Code', 'violent']].drop_duplicates())
crimes['year'] = crimes['Date'].transform(lambda date: date.year)
crimes['month'] = crimes['Date'].transform(lambda date: date.month)
crimes['day'] = crimes['Date'].transform(lambda date: date.day)
crimes['hour'] = crimes['Date'].transform(hourampm)
crimes['hour_old'] = crimes['hour']
crimes['hour'] = pd.Categorical(crimes['hour'], categories=['7AM', '8AM', '9AM', '10AM', '11AM', '12PM', '1PM', '2PM', '3PM', '4PM', '5PM', '6PM',
	'7PM', '8PM', '9PM', '10PM', '11PM', '12AM', '1AM', '2AM', '3AM', '4AM', '5AM', '6AM'], ordered=True)
print(crimes[['hour', 'hour_old']].drop_duplicates())
del crimes['hour_old']
print(crimes[['Date', 'year', 'month', 'day', 'hour']].iloc[random.sample(range(len(crimes)), 50)])

################################################################################
################################### PLOTS ######################################
################################################################################
for year in range(2009, 2018+1):
	plt.figure(figsize=(10, 14))
	monthname = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
		7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
	for month in range(1, 12+1):
		plt.subplot(4, 3, month)
		crimes.loc[(crimes.year == year) & (crimes.month == month)].groupby('hour')['violent'].sum().plot(kind='bar', color='black')
		plt.title(monthname[month])
		plt.xlabel('')
		indices = range(0, 24, 3)
		plt.xticks(indices, crimes['hour'].cat.categories[indices], rotation=60)
	plt.suptitle('Total Number of Violent Crimes by Month by Hour of Day, {}'.format(year))
	plt.tight_layout(pad=4.5)
	plt.savefig('crime-by-month-hour-{}.png'.format(year))



def plotnum(year, exclude):
	assert year >= 2009 & year <= 2018
	q, r = divmod(year-2009, 5)
	if not exclude: return (10*q) + r + 1
	else: return 5 + (10*q) + r + 1

f = plt.figure(figsize=(14, 10))
hsep = plt.Line2D((0, 1), (.5, .5), color='k', linewidth=5)
f.add_artist(hsep)
for year in range(2009, 2018+1):
	plt.subplot(4, 5, plotnum(year, False))
	crimes.loc[(crimes.year == year) & (crimes.month == 1)].groupby('hour')['violent'].sum().plot(kind='bar', color='black')
	plt.title('January {}'.format(year))
	plt.xlabel('')
	indices = range(0, 24, 3)
	plt.xticks(indices, crimes['hour'].cat.categories[indices], rotation=60)
	plt.subplot(4, 5, plotnum(year, True))
	crimes.loc[(crimes.year == year) & (crimes.month == 1) & (crimes.day != 1)].groupby('hour')['violent'].sum().plot(kind='bar', color='black')
	plt.title('January {}, Without Jan 1'.format(year))
	plt.xlabel('')
	indices = range(0, 24, 3)
	plt.xticks(indices, crimes['hour'].cat.categories[indices], rotation=60)
plt.suptitle('Total Number of Violent Crimes in January by Hour of Day, With and Without Jan 1')
plt.tight_layout(pad=4.5)
plt.savefig('crime-january-sensitivity.png')

