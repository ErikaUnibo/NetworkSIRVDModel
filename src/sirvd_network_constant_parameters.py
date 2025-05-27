from sirvd_network_model import SIRVD_NetworkModel

'''This module implements the SIRVD model on a network using constant parameters.'''
class SIRVD_NetworkConstantParameters(SIRVD_NetworkModel):
    def __init__(self, N: int, infection_rate: float, recovery_rate: float, fatality_rate: float, 
                 vaccination_rate: float, breakthrough_rate: float, graph_type: str, graph_params: dict = dict(), 
                 delta_t: int = 1, is_dynamic: bool = False):
        super().__init__(N, graph_type, graph_params, delta_t, is_dynamic)
        self.infection_rate = infection_rate
        self.vaccination_rate = vaccination_rate
        self.recovery_rate = recovery_rate
        self.fatality_rate = fatality_rate
        self.breakthrough_rate = breakthrough_rate


    def _evolve_node(self, node_id: int):
        self._evolve_node_state(node_id, self.infection_rate, self.vaccination_rate, self.fatality_rate, self.recovery_rate, self.breakthrough_rate)
        

    def _get_simulation_parameters(self):
        info = {
            'infection_rate': [],
            'recovery_rate' : [],
            'fatality_rate' : [],
            'vaccination_rate' : [],
            'breakthrough_rate': []
        }

        for t in range(self.time):
            info['infection_rate'].append(self.infection_rate)
            info['recovery_rate'].append(self.recovery_rate)
            info['fatality_rate'].append(self.fatality_rate)
            info['vaccination_rate'].append(self.vaccination_rate)
            info['breakthrough_rate'].append(self.breakthrough_rate)
        
        return info