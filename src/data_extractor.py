from data_reader import extract_COVID_data
import json
import os.path as path
from datetime import datetime

'''This module calls the data extraction and uses the SIRVD model to extract the variable parameters for the simulation.'''
def get_country_population(country):

    if country == 'Italy':
        return 60000000
    else:
        return -1

class DataExtractor:

    #TODO
    def __init__(self, country, average_recovery_time, average_breakthrough_time):

        self.COVID_country = country
        self.average_recovery_time = average_recovery_time
        self.average_breakthrough_time = average_breakthrough_time
        
        self.N = get_country_population(country)
        
        self.I = list()
        self.S = list()
        self.R = list()
        self.alpha = list()
        self.mu = list()
        self.psi = list()
        self.nu = list()
        self.sigma = list()


    def get_params(self, init_time = -1, end_time = -1, result_file = "extracted_data.json"):
        
        SIRVD_data = dict()
        if not path.exists(result_file):
            print("Extracting COVID parameters")
            self.__run_simulation()

            SIRVD_data = {'S': self.S, 'I': self.I, 'R': self.R, 'V': self.V, 'D': self.D,
                      'InfectionRate' : [alpha * self.N for alpha in self.alpha], 'FatalityRate': self.psi, 
                      'VaccinationRate': self.nu, 'RecoveryRate': self.mu, 'BreakthroughRate': self.sigma, 
                      'Time': self.Time}
            
            self.__save_data_to_json(SIRVD_data, result_file)
        else:
            SIRVD_data = self.__load_data_from_json(result_file)

        t_start = 0
        t_end = len(SIRVD_data['Time']) - 1

        if init_time != -1:
            while init_time > SIRVD_data['Time'][t_start]:
                t_start += 1
        if end_time != -1:
            while end_time > SIRVD_data['Time'][t_end]:
                t_end -=1

        out_data = {key : values_list[t_start:t_end] for key, values_list in SIRVD_data.items()}

        return out_data
    

    def __run_simulation(self):

        COVID_data = extract_COVID_data(self.COVID_country)

        start_covid = 0
        while COVID_data['I_new'][start_covid] < 1:
            start_covid += 1

        self.Time = COVID_data['Time'][start_covid+1:]
        self.V = COVID_data['V'][start_covid+1:]
        self.D = COVID_data['D'][start_covid+1:]
        self.I_new = COVID_data['I_new'][start_covid+1:]

        initial_infected = COVID_data['I_new'][start_covid]

        self.S.append(self.N - initial_infected)
        self.R.append(0)
        self.I.append(initial_infected)

        t = 0
        while (t < len(self.Time)-1):
            self.__extract_SIRVD_param(t)
            t += 1


    
    def __save_data_to_json(self, extracted_data, filename):
        
        if not filename.endswith('.json'):
            print(f"Error: format of file {filename} not supported (only JSON is valid)")
            return

        data_to_save = {
            'observables': {
                'Time': [datetime.strftime(date_time, "%Y/%m/%d") for date_time in extracted_data['Time']],
                'S': extracted_data['S'],
                'I': extracted_data['I'],
                'R': extracted_data['R'],
                'V': extracted_data['V'],
                'D': extracted_data['D']
            },
            'parameters': {
                'InfectionRate': extracted_data['InfectionRate'],
                'FatalityRate': extracted_data['FatalityRate'],
                'VaccinationRate': extracted_data['VaccinationRate'],
                'RecoveryRate': extracted_data['RecoveryRate'],
                'BreakthroughRate': extracted_data['BreakthroughRate'],
            }
        }

        with open(filename, 'w') as f:
            json.dump(data_to_save, f, indent=4)

        print(f"Data extracted and saved in: {filename}")


    def __load_data_from_json(self, filename):
        
        data = dict()
        with open(filename, 'r') as f:
            data_file = json.load(f)

            for key in data_file['observables']:
                if key == 'Time':
                    data[key] = [datetime.strptime(time_data, "%Y/%m/%d") for time_data in data_file['observables']['Time']]
                else:
                    data[key] = data_file['observables'][key]
            
            data.update(data_file['parameters'])

        return data
    

    def __extract_SIRVD_param(self, t):
        N = self.N

        D_dot = self.D[t+1] - self.D[t]
        V_dot = self.V[t+1] - self.V[t]

        S_t = self.S[t]
        I_t = self.I[t]
        R_t = self.R[t]
        I_new = self.I_new[t+1]

        psi_t = D_dot / I_t if D_dot != 0 else 0
        nu_t = V_dot / S_t
        mu_t = 1. / self.average_recovery_time
        alpha_t = I_new / (S_t * I_t) if I_new != 0 else 0
        sigma_t = 1. / self.average_breakthrough_time if self.average_breakthrough_time != -1 else 0

        S_t_future = S_t - I_new - V_dot + sigma_t * R_t
        I_t_future = I_t + I_new - mu_t*I_t - psi_t * I_t
        R_t_future = mu_t*I_t + R_t - sigma_t * R_t

        self.psi.append(psi_t)
        self.mu.append(mu_t)
        self.sigma.append(sigma_t)
        self.nu.append(nu_t)
        self.alpha.append(alpha_t)
        self.S.append(S_t_future)
        self.R.append(R_t_future)
        self.I.append(I_t_future)
