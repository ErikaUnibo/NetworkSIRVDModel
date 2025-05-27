# A Network approach on Epidemics: adapting the SIRVD Model to different types of Networks

In this repository, you will find a python implementation of the SIRVD model in its compartmental version and adapted to three different kind of networks: Erdős-Renyi, Watts-Strogatz and Barabási-Albert.

In `src` you will find the source files of the project divided in different modules.

In `src/Data` you will find the files containing the necessary data for the simulation with SIRVD parameters varying with time (extracted from COVID-19 real world data).

The relation can be found in `relation.pdf`. This project was made together with Katja Brunelli.

## How to run it

The module to launch is `main.py` in which you can choose the simulation you want to run (compartmental SIRVD, network SIRVD with constant parameters and network SIRVD with non-constant parameters) and abilitate/disabilitate the different additional features. 

## Requirements

In `requirements.txt` you will find the required packages to run the simulation.
