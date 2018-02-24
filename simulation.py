# -*- coding: utf-8 -*-
"""
The formation of Transitive Memory System (TMS)

This is based on the netlogo version of formation of TMS, except that the
function "productivity_TMS" was added to test how productive the teams are.

Author: Xiaoyi Yuan
Date: 08/06/2016

OS: Mac 10.10.5
Python Version: 3.5
"""

import random
import statistics
import networkx as nx
import csv

G = nx.DiGraph()

"""
7 kinds of areas, each corresponds with a color in the list
when connect with an expert, the edge becomes the corresponding color.
"""
colors = ['red', 'blue', 'green', 'yellow', 'white', 'cyan', 'pink']


class Agent(object):
    def __init__(self,
                 expertise, tasks, waitlist, availability, tertius, steps):
        self.expertise = expertise
        self.tasks = tasks
        self.waitlist = waitlist
        self.availability = availability
        self.tertius = tertius
        self.steps = steps


# First, create a team
def create_TMS(nagents, nareas, ntasks):

    agents = [Agent(expertise=[statistics.median
                               ([0, 1, random.normalvariate(0.5, 0.4)])
                               for i in range(nareas)],
                    tasks=[random.randint(0, nareas - 1)
                           for i in range(ntasks)],
                    availability=False,
                    waitlist=[],
                    tertius=0,
                    steps=0) for i in range(nagents)]

    G.add_nodes_from(agents)

    for agent in agents:
        others = [i for i in agents if i != agent]
        complete = 0
        for task in agent.tasks:
            # if the agent is an expert him/herself, complete the task
            if agent.expertise[task] > 0.5:
                complete = complete + 1
            else:
                # if there's an expert in the team that has helped him/her
                edge_colors = [G[agent][expert]['color']
                               for expert in G.successors(agent)]
                if colors[task] in edge_colors:
                    complete = complete + 1
                # if not connected to an expert
                else:
                    # find an expert and build an edge
                    experts = [expert for expert in others if
                               agent.expertise[task]
                               + expert.expertise[task] > 0.5]
                    if experts != []:
                        expert = random.choice(experts)
                        G.add_edge(agent, expert, color=colors[task])
                        complete = complete + 1
        # white nodes: completed all their tasks; black node: who didn't
        if complete == ntasks:
            nx.set_node_attributes(G, 'color', {agent: 'white'})
        else:
            nx.set_node_attributes(G, 'color', {agent: 'black'})

    # check if anyone in the network is in tertius position.
    # if it is, then agent.tertius= 1, otherwise, remain 0.
    for agent in agents:
        # check if all its outdegree neighbors are a transitive triad
        outdegree = []
        for i in G.successors(agent):
            outdegree.append(i)
        if len(outdegree) > 1:
            for i in outdegree:
                for n in outdegree:
                    if n != i and \
                            n in G.predecessors(i) or n in G.successors(i):
                        agent.tertius = 1

    return G, agents, nareas, nagents

'''
Next, test TMS on its productivity:
This step involves parallel activation.
Every team member activates at the same time
'''


def productivity_TMS(ntasks):
    # Assign them a new set of tasks to test their productivity
    for agent in team:
        agent.tasks = [random.randint(0, number_of_areas - 1)
                       for i in range(ntasks)]
        agent.steps = 0
    steps = 0
    while steps <= 1000:
        for member in team:
            # I n each step, each person is available in the beginning
            # but only available for dealing with only one task
            member.availability = True
            if member.tasks == [] and member.steps == 0:
                member.steps = steps
            # if this member hasn't done with all the tasks,
            # if he can do it on his own, do it and then become unavailable
            if member.tasks != [] and member.expertise[member.tasks[0]] > 0.5:
                del member.tasks[0]
                member.availability = False
            # if he cannot do it on his own, add the task to expert's waitlist
            if member.tasks != [] and \
                    member.expertise[member.tasks[0]] <= 0.5:
                if any(G.successors(member)):
                    for expert in G.successors(member):
                        if G[member][expert]['color'] == \
                                colors[member.tasks[0]] and \
                                member not in expert.waitlist:
                            expert.waitlist.append(member)

        # for those who cannot do his own tasks, check if he can help others
        for member in team:
            if member.tasks != [] and \
                    member.availability and \
                    any(member.waitlist):
                del member.waitlist[0].tasks[0]
                del member.waitlist[0]
        steps = steps + 1


with open("output.csv", 'w') as csvfile:
    writer = csv.writer(csvfile)
    for n in range(1000):
        G, team, number_of_areas, number_of_agents = create_TMS(10, 5, 10)
        productivity_TMS(10)
        for i in team:
            result = writer.writerow([i.tertius, i.steps])

'''
TMS triadic census
'''
nx.triadic_census(G)