from sirvd_network_model import SIRVD_NetworkModel

'''This module implements the SIRVD model on a network using parameters which vary with time.'''
class SIRVD_NetworkVariableParameters(SIRVD_NetworkModel):
    def __init__(self, N: int, graph_type: str, infection_rate_schedule: list, recovery_rate_schedule: list,
                 fatality_rate_schedule: list, vaccination_rate_schedule: list, breakthrough_rate_schedule: list, 
                 graph_params: dict = dict(), delta_t: int = 1, is_dynamic: bool = False):
        super().__init__(N, graph_type, graph_params, delta_t, is_dynamic)

        self.infection_rate_schedule = infection_rate_schedule
        self.recovery_rate_schedule = recovery_rate_schedule
        self.fatality_rate_schedule = fatality_rate_schedule
        self.vaccination_rate_schedule = vaccination_rate_schedule
        self.breakthrough_rate_schedule = breakthrough_rate_schedule

        check_1_ok = len(self.infection_rate_schedule) == len(self.recovery_rate_schedule)
        check_2_ok = len(self.recovery_rate_schedule) == len(self.fatality_rate_schedule)
        check_3_ok = len(self.fatality_rate_schedule) == len(self.vaccination_rate_schedule)
        check_4_ok = len(self.vaccination_rate_schedule) == len(breakthrough_rate_schedule)

        if not (check_1_ok and check_2_ok and check_3_ok and check_4_ok):
            print("Error: scheduled data are not of the same length")
            exit()


    def _evolve_node(self, node_id: int):

        if self.time >= len(self.infection_rate_schedule):
            print('Error: simulation time longer than available parameters data')
            return

        current_infection_rate = self.infection_rate_schedule[self.time]
        current_recovery_rate = self.recovery_rate_schedule[self.time]
        current_fatality_rate = self.fatality_rate_schedule[self.time]
        current_vaccination_rate = self.vaccination_rate_schedule[self.time]
        current_breakthrough_rate = self.breakthrough_rate_schedule[self.time]

        self._evolve_node_state(node_id, current_infection_rate, current_vaccination_rate, current_fatality_rate,
                                 current_recovery_rate, current_breakthrough_rate)
    

    def _get_simulation_parameters(self):
        info = dict()
        if self.infection_rate_schedule:
            info['infection_rate'] = self.infection_rate_schedule
        if self.recovery_rate_schedule:
            info['recovery_rate'] = self.recovery_rate_schedule
        if self.fatality_rate_schedule:
            info['fatality_rate'] = self.fatality_rate_schedule
        if self.vaccination_rate_schedule:
            info['vaccination_rate'] = self.vaccination_rate_schedule
        if self.breakthrough_rate_schedule:
            info['breakthrough_rate'] = self.breakthrough_rate_schedule
        
        return info
