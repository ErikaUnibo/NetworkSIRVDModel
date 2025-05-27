import numpy as np
from enum import Enum
from abc import ABC, abstractmethod
import json
import sys

'''This module defines the basic functioning structure of a SIRVD simulation model. In particular it defines the execution structure and 
   the computation of results data.'''
class State(Enum):
    SUSCEPTIBLE = "S"
    INFECTED = "I"
    RECOVERED = "R"
    VACCINATED = "V"
    DEAD = "D"


class SIRVD_Base(ABC):
    def __init__(self, N: int, delta_t: int = 1):

        self.delta_t = delta_t
        self.time = 0

        self.observables = {'Time': [], State.SUSCEPTIBLE: [], State.INFECTED:[], State.RECOVERED :[], State.VACCINATED :[], State.DEAD :[]}
        self.daily_new_inftected = []
        self.population = N

    @abstractmethod
    def _record_state(self):
        pass

    @abstractmethod
    def _evolve(self, lockdowns=None, events=None):
        pass

    @abstractmethod
    def _get_simulation_parameters(self):
        pass

    @abstractmethod
    def _initialize_infection(self, number_of_infectious, target_higher, target_lower):
        pass


    def __extract_additional_data(self):

        self.epidemy_duration = len(self.observables['Time'])
        for t in range(len(self.observables['Time'])):
            if self.observables[State.INFECTED][t] < 1 and t > 0:
                self.epidemy_duration = self.observables['Time'][t]
                break

        # Reproduction rate extraction

        self.reproduction_rate = [0]
        for t in range(1, self.epidemy_duration):
            new_infected = self.daily_new_inftected[t]
            reproduction_rate = abs(new_infected) / self.observables[State.INFECTED][t-1]
            self.reproduction_rate.append(reproduction_rate)

        infected_peak_index = np.argmax(self.observables[State.INFECTED])
        self.infected_peak_time = self.observables['Time'][infected_peak_index]
        self.infected_peak = self.observables[State.INFECTED][self.infected_peak_time]

        total_number_of_infected = sum(self.daily_new_inftected)
        self.case_fatality_rate = self.observables[State.DEAD][-1] / total_number_of_infected


    def run_simulation(self, initial_infectious, simulation_time, result_filename = "simulation_results.json", lockdowns = None, events = None,
                       target_higher = False, target_lower = False):

        self._initialize_infection(initial_infectious, target_higher, target_lower)

        self.daily_new_inftected.append(initial_infectious)
        self._record_state()

        steps_number = int(np.round(simulation_time/self.delta_t))

        for t in range(steps_number):
            self.time += self.delta_t
            
            self.daily_new_inftected.append(0)
            self._evolve(lockdowns, events)
            self._record_state()
            self.__update_user_time()
        
        print('\nSimulation Terminated')

        self.__extract_additional_data()
        self.__save_results(result_filename)
        

    def __save_results(self, filename):
        observables_result = {}
        for key, value_list in self.observables.items():
            if isinstance(key, State):
                observables_result[key.value] = value_list
            else:
                observables_result[key] = value_list

        results = {
            'observables': observables_result,
            'additional_data': {
                'reproduction_rate': self.reproduction_rate,
                'infected_peak_time': self.infected_peak_time,
                'infected_peak': self.infected_peak,
                'epidemy_duration': self.epidemy_duration,
                'case_fatality_rate': self.case_fatality_rate
            },
            'parameters': self._get_simulation_parameters()
        }

        with open(filename, 'w') as f:
            json.dump(results, f)

        print(f"Result save in the file: {filename}")

    
    def __update_user_time(self):

        sys.stdout.write(f"\rSimulation at time {self.time}")
        sys.stdout.flush()
