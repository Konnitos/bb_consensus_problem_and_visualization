# Requirements
python3

pycryptodome 3.10.1 

pygame 2 

# Aim of the project
simulates a byzantine general network with random traitor activity using the Dolev-Strong authenticated broadcast protocal to reach consensus. the simulation uses pycryptodome to sign and validate message payloads. The final state of the network is then used to generate a replay of the network interaction built using pygame.

# How to use 
Currently just run visualization if you have everything installed.

if you just want the network simulation run bb_consensus_simulation.py. you must update the file to change the network setup currently

# Notes
The max number of nodes is currently 5 this was selected becuase going above this number caused the simulation to start to slow down 

if you have a high number of triators get ready for a long list of messages that need to be shown 