import networkx as nx
import numpy as np
import random
from abc import abstractmethod
from sirvd_base import SIRVD_Base, State

'''This module implements the basic structure for a SIRVD model simulation through a network approach.'''
class Person:
    def __init__(self, _node_index):
        self.node_index = _node_index
        self.state = State.SUSCEPTIBLE
        self.next_state = self.state


class SIRVD_NetworkModel(SIRVD_Base):
    def __init__(self, N:int, graph_type: str, graph_params: dict = None, delta_t: int = 1, is_dynamic: bool = False):
        super().__init__(N, delta_t)
        self.graph_type = graph_type
        self.is_dynamic = is_dynamic

        self.__create_graph(self.population, graph_params)

        self.people = {n: Person(n) for n in self.graph.nodes}


    def __create_graph(self, N: int, graph_params: dict):

        if self.graph_type == 'erdos_renyi':
            p = graph_params.get('p', 0.1)
            self.graph = nx.erdos_renyi_graph(N, p)
        elif self.graph_type == 'barabasi_albert':
            m = graph_params.get('m', 3)
            self.graph = nx.barabasi_albert_graph(N, m)
        elif self.graph_type == 'watts_strogatz':
            k = graph_params.get('k', 4)
            p = graph_params.get('p', 0.1)
            self.graph = nx.connected_watts_strogatz_graph(N, k, p)
        else:
            print("Unsupported graph type")
            exit()


    @abstractmethod
    def _evolve_node(self, n):
        pass


    def _record_state(self):
        self.observables[State.SUSCEPTIBLE].append(
            sum(1 for person in self.people.values()
                if person.state == State.SUSCEPTIBLE)
        )
        self.observables[State.INFECTED].append(
            sum(1 for person in self.people.values()
                if person.state == State.INFECTED)
        )
        self.observables[State.RECOVERED].append(
            sum(1 for person in self.people.values()
                if person.state == State.RECOVERED)
        )
        self.observables[State.VACCINATED].append(
            sum(1 for person in self.people.values()
                if person.state == State.VACCINATED)
        )
        self.observables[State.DEAD].append(
            sum(1 for person in self.people.values()
                if person.state == State.DEAD)
        )
        self.observables['Time'].append(self.time)


    def _evolve(self, lockdowns = None, events = None):

        for n in range(self.graph.number_of_nodes()):
            self._evolve_node(n)

        for person in self.people.values():
            person.state = person.next_state

        if self.is_dynamic:
            self.__evolve_dynamic(lockdowns, events)


    def _initialize_infection(self, number_of_infectious, target_higher, target_lower):
        
        initial_nodes = list()
        if target_higher:
            nodes_degree = list(dict(self.graph.degree()).values())
            while len(initial_nodes) < number_of_infectious:
                target_node = np.argmax(nodes_degree)
                initial_nodes.append(target_node)
                nodes_degree[target_node] = -1
        elif target_lower:
            nodes_degree = list(dict(self.graph.degree()).values())
            while len(initial_nodes) < number_of_infectious:
                target_node = np.argmin(nodes_degree)
                initial_nodes.append(target_node)
                nodes_degree[target_node] = self.population
        else:
            initial_nodes = random.sample(list(self.graph.nodes), number_of_infectious)

        for node in initial_nodes:
            self.people[node].state = State.INFECTED


    def __evolve_network_structure(self, add_prob=0.01, remove_prob=0.01):

        nodes = list(self.graph.nodes())

        edges_to_add = int(self.graph.number_of_edges() * add_prob)
        edges_to_remove = int(self.graph.number_of_edges() * remove_prob)

        new_edges = []
        new_edges_count = 0
        while new_edges_count < edges_to_add:
            u, v = random.sample(nodes, 2)
            if u != v and not self.graph.has_edge(u, v) and (u,v) not in new_edges:
                new_edges.append((u,v))
                new_edges.append((v,u))
                new_edges_count += 1

        removable_edges = []
        removable_edges_count = 0
        edges = list(self.graph.edges())
        random.shuffle(edges)
        while removable_edges_count < edges_to_remove:
            u, v = edges.pop()
            if (u, v) not in removable_edges:
                removable_edges.append((u,v))
                removable_edges.append((v,u))
                removable_edges_count += 1
        
        self.graph.add_edges_from(new_edges)
        self.graph.remove_edges_from(removable_edges)


    def __apply_lockdown(self, reduction_factor=0.9):

        num_edges_to_remove = int(self.graph.number_of_edges() * reduction_factor)

        removable_edges = []
        removable_edges_count = 0
        edges = list(self.graph.edges())
        random.shuffle(edges)
        while removable_edges_count < num_edges_to_remove:
            u, v = edges.pop()
            if (u, v) not in removable_edges:
                removable_edges.append((u,v))
                removable_edges.append((v,u))
                removable_edges_count += 1

        self.graph.remove_edges_from(removable_edges)

        self.lockdown_edges = removable_edges


    def __end_lockdown(self):

        self.graph.add_edges_from(self.lockdown_edges)
        self.lockdown_edges.clear()


    def __apply_event(self, aggregation_rate=0.5):

        nodes = list(self.graph.nodes())
        edges_to_add = int(self.graph.number_of_edges() * aggregation_rate)

        new_edges = []
        new_edges_count = 0
        while new_edges_count < edges_to_add:
            u, v = random.sample(nodes, 2)
            if u != v and not self.graph.has_edge(u, v) and (u,v) not in new_edges:
                new_edges.append((u,v))
                new_edges.append((v,u))
                new_edges_count += 1

        self.graph.add_edges_from(new_edges)
        self.event_edges = new_edges


    def __remove_event(self):

        self.graph.remove_edges_from(self.event_edges)
        self.event_edges.clear()


    def __evolve_dynamic(self, lockdowns, events):
        if lockdowns:
            for start, end in lockdowns:
                if self.time == start:
                    self.__apply_lockdown()
                elif self.time == end:
                    self.__end_lockdown()

        if events:
            for start, end in events:
                if self.time == start:
                    self.__apply_event()
                if self.time == end:
                    self.__remove_event()

        self.__evolve_network_structure()
    

    def _evolve_node_state(self, node_id: int, infection_rate: float, vaccination_rate: float, fatality_rate: float, 
                      recovery_rate: float, breakthrough_rate: float):
        
        current_state = self.people[node_id].state
        next_state = current_state

        if current_state == State.SUSCEPTIBLE:
            degree = self.graph.degree(node_id)

            if degree != 0:
                infected_neighbors = sum(
                    1 for neighbor in self.graph.neighbors(node_id)
                    if self.people[neighbor].state == State.INFECTED
                )
                total_infection_prob = (infection_rate * infected_neighbors / degree) * self.delta_t
            else:
                total_infection_prob = 0

            vaccination_prob = vaccination_rate * self.delta_t
            
            random_number = random.random()

            if random_number < total_infection_prob:
                next_state = State.INFECTED
                self.daily_new_inftected[self.time] += 1
            elif (random_number - total_infection_prob) < vaccination_prob:
                next_state = State.VACCINATED

        elif current_state == State.INFECTED:            

            random_number = random.random()
            fatality_prob = fatality_rate * self.delta_t
            recovery_prob = recovery_rate * self.delta_t
            
            if random_number < fatality_prob:
                next_state = State.DEAD
            elif (random_number - fatality_prob) < recovery_prob:
                next_state = State.RECOVERED

        elif current_state == State.RECOVERED:
            
            random_number = random.random()
            breakthrough_prob = breakthrough_rate * self.delta_t

            if random_number < breakthrough_prob:
                next_state = State.SUSCEPTIBLE

        self.people[node_id].next_state = next_state
        