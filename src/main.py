from sirvd_network_constant_parameters import SIRVD_NetworkConstantParameters
from sirvd_network_variable_parameters import SIRVD_NetworkVariableParameters
from sirvd_compartmental_model import SIRVD_CompartmentalModel
from data_extractor import DataExtractor
from sirvd_plotter import SIRVD_Plotter
from datetime import datetime

POPULATION = 2000


def run_constant_network_model(graph_type, graph_parameters, infection_rate, vaccination_rate, fatality_rate, 
                               breakthrough_rate, recovery_rate, simulation_time, delta_days, initial_infected,
                               result_file = 'SIRVD_network_constant.json', is_dynamic = False, lockdowns = None, events = None,
                               target_higher = False, target_lower = False):
    
    sirvd_model = SIRVD_NetworkConstantParameters(N=POPULATION, infection_rate=infection_rate, recovery_rate=recovery_rate, 
                                                  fatality_rate=fatality_rate, vaccination_rate=vaccination_rate, 
                                                  breakthrough_rate=breakthrough_rate, graph_type=graph_type, graph_params=graph_parameters,
                                                  delta_t=delta_days, is_dynamic=is_dynamic)
    
    sirvd_model.run_simulation(initial_infectious=initial_infected, simulation_time=simulation_time,
                               result_filename=result_file, lockdowns=lockdowns, events=events, target_higher=target_higher, target_lower=target_lower)
    

def run_dynamic_network_model(graph_type, graph_parameters, infection_rate, vaccination_rate, fatality_rate, breakthrough_rate,
                              recovery_rate, simulation_time, delta_days, initial_infected, 
                              result_file = 'SIRVD_network_variable.json', is_dynamic = False, lockdowns = None, events = None,
                              target_higher = False, target_lower = False):
    
    sirvd_model = SIRVD_NetworkVariableParameters(N=POPULATION, graph_type=graph_type, graph_params=graph_parameters,
                                                  delta_t=delta_days, is_dynamic=is_dynamic, infection_rate_schedule=infection_rate,
                                                  recovery_rate_schedule=recovery_rate, fatality_rate_schedule=fatality_rate,
                                                  vaccination_rate_schedule=vaccination_rate, breakthrough_rate_schedule=breakthrough_rate)
    
    sirvd_model.run_simulation(initial_infectious=initial_infected, simulation_time=simulation_time,
                               result_filename=result_file, lockdowns=lockdowns, events=events, target_higher=target_higher, target_lower=target_lower)
    

def run_compartmental_model(infection_rate, vaccination_rate, fatality_rate, breakthrough_rate, recovery_rate, 
                             simulation_time, delta_days, initial_infected, result_file = 'SIRVD_network_constant.json'):
    
    sirvd_model = SIRVD_CompartmentalModel(N=POPULATION, beta=infection_rate, mu=recovery_rate, nu=vaccination_rate,
                                            psi=fatality_rate, sigma=breakthrough_rate, delta_t=delta_days)
    
    sirvd_model.run_simulation(initial_infectious=initial_infected, simulation_time=simulation_time,
                               result_filename=result_file)


def get_variable_parameters(filename, country, start_time, end_time, 
                            average_backthrough_time, average_recovery_time) -> dict:

    parameter_extractor = DataExtractor(country, average_recovery_time, average_backthrough_time)

    extracted_data = parameter_extractor.get_params(start_time, end_time, filename)

    return extracted_data


if __name__ == '__main__':

    enable_compartmental_model = False
    enable_network_constant_model = True
    enable_network_variable_model = False

    # Network Info
    graph_type = 'watts_strogatz'
    graph_parameters = {'k':6,'p':0.03}
    is_dynamic = True
    target_higher = False
    target_lower = False

    # SIRVD constant Model parameters
    infection_rate = 0.5
    vaccination_rate = 0.03
    fatality_rate = 0.01
    breakthrough_rate = 0.2
    recovery_rate = 0.1

    # Simulation parameters
    duration = 300 # Days
    delta_days = 1 # Step of simulation
    initial_infected = 200

    # For Dynamic network
    lockdowns = [(15, 60)]
    events = [(1, 10)]

    # For variable parameters
    country = 'Italy'
    start_time = datetime(2020, 10, 1)
    end_time = datetime(2022, 12, 31)
    average_backtrhrough_time = 30
    average_recovery_time = 7

    plotter = SIRVD_Plotter()

    if enable_compartmental_model:
        print("SIMULATING COMPARTMENTAL MODEL")
    
        compartimental_result_file = 'Data/Compartimental_result_file_variable2.json'

        run_compartmental_model(infection_rate, vaccination_rate, fatality_rate, breakthrough_rate, recovery_rate, duration, delta_days, initial_infected, compartimental_result_file)

        plotter.plot_from_file(compartimental_result_file, 'Compartmental Numerical Simulation')


    if enable_network_constant_model:
        print("SIMULATING CONSTANT PARAMETERS NETWORK")

        constant_network_result_file = 'Data/Constant_network_result_file_wsboth.json'

        run_constant_network_model(graph_type, graph_parameters, infection_rate, vaccination_rate, fatality_rate,
                                   breakthrough_rate, recovery_rate, duration, delta_days, initial_infected, constant_network_result_file,
                                   is_dynamic, lockdowns, events, target_higher, target_lower)
    

        plotter.plot_from_file(constant_network_result_file, 'Watts Strogatz Network Simulation')


    if enable_network_variable_model:
        print("SIMULATING VARIABLE PARAMETERS NETWORK")

        variable_network_result_file = 'Data/Variable_network_result_file_er3.json'

        variable_parameter_file = 'Data/COVID_parameter.json'

        variable_parameters = get_variable_parameters(variable_parameter_file, country,
                                                     start_time, end_time, average_backtrhrough_time, average_recovery_time)
        
        effective_duration = (end_time-start_time).days

        run_dynamic_network_model(graph_type, graph_parameters, variable_parameters['InfectionRate'], variable_parameters['VaccinationRate'],
                                  variable_parameters['FatalityRate'], variable_parameters['BreakthroughRate'], variable_parameters['RecoveryRate'],
                                  effective_duration, delta_days, initial_infected, variable_network_result_file, is_dynamic, lockdowns, events, target_higher, target_lower)
    
        plotter.plot_from_file(variable_network_result_file, 'Erdos Renyi Variable Network Simulation')

