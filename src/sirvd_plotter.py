import matplotlib.pyplot as plt
import json
from sirvd_network_model import State

COLOR_SUSCEPTIBLE = 'blue'
COLOR_INFECTED = 'orange'
COLOR_RECOVERED = 'green'
COLOR_VACCINATED = 'purple'
COLOR_DEAD = 'grey'
COLOR_REPRODUCTION_RATE = 'black'

class SIRVD_Plotter:
    def __init__(self):
        pass

    def plot_from_data(self, data: dict, title: str = 'Simulation Results'):
        times = data.get('Time', [])
        if not times:
            print("Warning: No 'Time' data found for plotting.")
            return

        plt.figure()
        state_colors = {
            State.SUSCEPTIBLE: COLOR_SUSCEPTIBLE,
            State.INFECTED: COLOR_INFECTED,
            State.RECOVERED: COLOR_RECOVERED,
            State.VACCINATED: COLOR_VACCINATED,
            State.DEAD: COLOR_DEAD
        }

        for state_name, color in state_colors.items():
            values = data.get(state_name.value, [])
            if values:
                plt.plot(times, values, label=state_name, color=color)

        plt.xlabel('Time')
        plt.ylabel('Number of People')
        plt.title(title + ' - State Evolution')
        plt.legend()
        plt.grid(True)
        plt.show()

        reproduction_rate = data.get('reproduction_rate', [])
        plt.figure()
        plt.plot(range(len(reproduction_rate)), reproduction_rate, label='Reproduction Rate', color=COLOR_REPRODUCTION_RATE)
        plt.xlabel('Time')
        plt.ylabel('Reproduction Rate')
        plt.title(title + ' - Reproduction Rate')
        plt.grid(True)
        plt.legend()
        plt.show()


    def plot_from_file(self, filename="simulation_results.json", title='Simulation Results'):
        try:
            with open(filename, 'r') as f:
                results = json.load(f)
                observables = results.get('observables', {})
                additional_data = results.get('additional_data', {})

                plot_data = observables.copy()
                plot_data.update(additional_data)
                self.plot_from_data(plot_data, title)

        except FileNotFoundError:
            print(f"Error: File not found at {filename}")
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {filename}")