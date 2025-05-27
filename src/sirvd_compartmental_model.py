from sirvd_base import SIRVD_Base, State

'''This module implements the compartmental version of the SIRVD model.'''
class SIRVD_CompartmentalModel(SIRVD_Base):
    def __init__(self, N, beta, mu, nu, psi, sigma, delta_t):
        super().__init__(N, delta_t)
        # Inizializzazione
        self.beta = beta
        self.mu = mu
        self.nu = nu
        self.psi = psi
        self.sigma = sigma

        self.infected = 0
        self.susceptibles = 0
        self.deceased = 0
        self.recovered = 0
        self.vaccinated = 0


    def _record_state(self):
        
        self.observables[State.SUSCEPTIBLE].append(self.susceptibles)
        self.observables[State.INFECTED].append(self.infected)
        self.observables[State.RECOVERED].append(self.recovered)
        self.observables[State.VACCINATED].append(self.vaccinated)
        self.observables[State.DEAD].append(self.deceased)
        self.observables['Time'].append(self.time)    


    def _evolve(self, lockdowns = None, events = None):

        if (lockdowns or events):
            print("Compartimental model does not support lockdowns and events")
            exit()


        N_total = self.susceptibles + self.deceased + self.recovered + self.infected + self.vaccinated

        S_future = (((-self.beta * self.susceptibles * self.infected / N_total - self.nu * self.susceptibles + self.sigma * self.recovered) * self.delta_t)) + self.susceptibles
        I_future = (((self.beta * self.susceptibles * self.infected / N_total - self.mu * self.infected - self.psi * self.infected) * self.delta_t)) + self.infected
        R_future = (((self.mu * self.infected - self.sigma * self.recovered) * self.delta_t)) + self.recovered
        V_future = (((self.nu * self.susceptibles) * self.delta_t)) + self.vaccinated
        D_future = (((self.psi * self.infected) * self.delta_t)) + self.deceased

        self.daily_new_inftected[self.time] += self.beta * self.susceptibles * self.infected / N_total

        self.susceptibles = S_future
        self.infected = I_future
        self.recovered = R_future
        self.vaccinated = V_future
        self.deceased = D_future

    
    def _get_simulation_parameters(self):

        info = {
            'infection_rate': [],
            'recovery_rate' : [],
            'fatality_rate' : [],
            'vaccination_rate' : [],
            'breakthrough_rate': []
        }

        for t in range(self.time):
            info['infection_rate'].append(self.beta)
            info['recovery_rate'].append(self.mu)
            info['fatality_rate'].append(self.psi)
            info['vaccination_rate'].append(self.nu)
            info['breakthrough_rate'].append(self.sigma)
        
        return info

    
    def _initialize_infection(self, number_of_infectious, target_higher, target_lower):

        if target_higher or target_lower:
            print('Warning: compartimental model does not support targeted infection')

        self.infected = number_of_infectious
        self.susceptibles = self.population - number_of_infectious