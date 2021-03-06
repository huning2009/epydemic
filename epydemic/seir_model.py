# SEIR as a compartmented model
#
# Copyright (C) 2017--2020 Simon Dobson
# 
# This file is part of epydemic, epidemic network simulations in Python.
#
# epydemic is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# epydemic is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with epydemic. If not, see <http://www.gnu.org/licenses/gpl.html>.

from epydemic import CompartmentedModel

class SEIR(CompartmentedModel):
    '''The Susceptible-Exposed-Infected-Removed :term:`compartmented model of disease`.
    A susceptible node becomes exposed when infected by either an exposed or an infected
    neighbour. Exposed nodes become infected (symptomatic) to infected and then recover
    to removed.
    
    In contrast to the more familiar :class:`SIR` model, SEIR has two
    compartments that can pass infection. The utility of the model from two aspects:
    exploring what fraction of the contract tree arises from infected individuals
    *versus* exposed individuals, capturing the significance of asymptomatic infection;
    and allowing countermeasures to be applied to symptomatic individuals whose presence
    could be more easily detected than those who are exposed by asymptomatic.

    The SERI model in `epydemic` is very flexible, allowing different infection probabilities
    for susceptible-exposed or susceptible-infected interactions. The initial seed population
    is placed into :attr:`EXPOSED`, rather than into :attr:`INFECTED` as happens
    for :class:`SIR`.'''
    
    # Model parameters
    P_EXPOSED = 'epydemic.SEIR.pExposed'              #: Parameter for probability of initially being exposed.
    P_INFECT_ASYMPTOMATIC = 'epydemic.SEIR.pInfectA'  #: Parameter for probability of infection on contact with an exposed individual
    P_INFECT_SYMPTOMATIC = 'epydemic.SEIR.pInfect'    #: Parameter for probability of infection on contact with a symptomatic individual.
    P_SYMPTOMS = 'epydemic.SEIR.pSymptoms'            #: Parameter for probability of becoming symptomatic after exposure. 
    P_REMOVE = 'epydemic.SEIR.pRemove'                #: Parameter for probability of removal (recovery).
    
    # Possible dynamics states of a node for SIR dynamics
    SUSCEPTIBLE = 'epydemic.SEIR.S'        #: Compartment for nodes susceptible to infection.
    EXPOSED = 'epydemic.SEIR.E'           #: Compartment for nodes exposed and infectious.
    INFECTED = 'epydemic.SEIR.I'           #: Compartment for nodes symptomatic and infectious.
    REMOVED = 'epydemic.SEIR.R'            #: Compartment for nodes recovered/removed.

    # Locus containing the edges at which dynamics can occur
    SE = 'epydemic.SEIR.SE'                #: Edge able to transmit infection from an exposed individual.
    SI = 'epydemic.SEIR.SI'                #: Edge able to transmit infection from an infected individual.

    def __init__( self ):
        super(SEIR, self).__init__()

    def build( self, params ):
        '''Build the SEIR model.

        :param params: the model parameters'''
        super(SEIR, self).build(params)

        pExposed = params[self.P_EXPOSED]
        pInfectA = params[self.P_INFECT_ASYMPTOMATIC]
        pInfect = params[self.P_INFECT_SYMPTOMATIC]
        pSymptoms = params[self.P_SYMPTOMS]
        pRemove = params[self.P_REMOVE]

        self.addCompartment(self.SUSCEPTIBLE, 1.0 - pExposed)
        self.addCompartment(self.EXPOSED, pExposed)
        self.addCompartment(self.INFECTED, 0.0)
        self.addCompartment(self.REMOVED, 0.0)

        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.EXPOSED, name=self.SE)
        self.trackEdgesBetweenCompartments(self.SUSCEPTIBLE, self.INFECTED, name=self.SI)
        self.trackNodesInCompartment(self.EXPOSED)
        self.trackNodesInCompartment(self.INFECTED)

        self.addEventPerElement(self.SE, pInfectA, self.infectAsymptomatic)
        self.addEventPerElement(self.SI, pInfect, self.infect)
        self.addEventPerElement(self.EXPOSED, pSymptoms, self.symptoms)
        self.addEventPerElement(self.INFECTED, pRemove, self.remove)

    def infectAsymptomatic( self, t, e ):
        '''Perform an infection event when an :attr:`EXPOSED` individual infects
        a neighbouring :attr:`SUSCEPTIBLE`, rendering them :attr:`EXPOSED` in turn.  
        The default calls :meth:`infect` so that infections by way of exposed ir
        symptomatic individuals are treated in the same way. Sub-classes can override this
        to, for example, record that the infection was passed asymptomatically.

        :param t: the simulation time
        :param e: the edge transmitting the infection'''
        self.infect(t, e)

    def infect( self, t, e ):
        '''Perform an infection event when an :attr:`INFECTED` individual infects
        a neighbouring :attr:`SUSCEPTIBLE`, rendering them :attr:`EXPOSED` in turn.  
        
        :param t: the simulation time
        :param e: the edge transmitting the infection'''
        (n, _) = e
        self.changeCompartment(n, self.EXPOSED)
        self.markOccupied(e, t)

    def symptoms( self, t, n ):
        '''Perform the symptoms-developing event. This changes the compartment of
        the node to :attr:`INFECTED`.

        :param t: the simulation time (unused)
        :param n: the node'''
        self.changeCompartment(n, self.INFECTED)

    def remove( self, t, n ):
        '''Perform a removal event. This changes the compartment of
        the node to :attr:`REMOVED`.

        :param t: the simulation time (unused)
        :param n: the node'''
        self.changeCompartment(n, self.REMOVED)
    
                
   
