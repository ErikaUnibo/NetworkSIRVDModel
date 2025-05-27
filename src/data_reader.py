import csv
from datetime import datetime, timedelta

'''This module defines the functionalities to extract COVID data given a certain country.'''
def read_data_from_file(path_to_file: str):

    data = {'Country': [], 'Day': [], 'Data': []}
    with open(path_to_file) as file:
        row_iterator = csv.DictReader(file, delimiter=',')

        for row in row_iterator:
            data['Country'].append(row['Entity'])
            data['Day'].append(datetime.strptime(row['Day'], "%Y-%m-%d"))
            data['Data'].append(float(row['Data']))

    return data

def filter_from_country(data: dict, country: str):

    country_set = set(data['Country'])

    if country not in country_set:
        print('Error: country not present in data')
        return dict()

    out_data = {'Day': [], 'Data': []}    
    for i in range(len(data['Country'])):
        if data['Country'][i] == country:
            out_data['Day'].append(data['Day'][i])
            out_data['Data'].append(data['Data'][i])

    return out_data


def align_time_data(list_of_data: dict, start_time = None, end_time = None):

    if start_time == None:
        min_time = min([data['Day'][0] for data in list_of_data.values()])
    else:
        min_time = start_time

    if end_time == None:
        max_time = min([data['Day'][-1] for data in list_of_data.values()])
        max_time -= timedelta(1)
    else:
        max_time = end_time

    new_data = {'Time': []}
    current_time = min_time
    while current_time <= max_time:
        new_data['Time'].append(current_time)
        current_time += timedelta(days=1)

    for key in list_of_data:

        new_data[key] = list()
        current_time = min_time
        current_start_time = list_of_data[key]['Day'][0]

        while current_time < current_start_time:
            new_data[key].append(0.0)
            current_time += timedelta(days=1)

        i = 0
        while current_time <= max_time:
            if current_time in list_of_data[key]['Day']:
                if key == 'D' and len(new_data[key]) != 0:
                    new_data[key].append(list_of_data[key]['Data'][i] + new_data[key][-1])
                else:
                    new_data[key].append(list_of_data[key]['Data'][i])
                i += 1
            else:
                new_data[key].append(new_data[key][-1])
            current_time += timedelta(days=1)

    return new_data


def extract_COVID_data(country: str):

    deaths = read_data_from_file('./Data/deaths.csv')
    vaccinated = read_data_from_file('./Data/vaccinated.csv')
    infected = read_data_from_file('./Data/infected_cases.csv')

    deaths_country = filter_from_country(deaths, country)
    vaccinated_country = filter_from_country(vaccinated, country)
    infected_country = filter_from_country(infected, country)

    data = {'D': deaths_country, 'V': vaccinated_country, 'I_new': infected_country}

    return align_time_data(data)




