
from .yakindumm import getEClassifier, eClassifiers
from .yakindumm import name, nsURI, nsPrefix, eClass
from .yakindumm import Pseudostate, Vertex, Region, Transition, Statechart, Entry, Synchronization, State, RegularState, CompositeElement, Choice, Exit, FinalState


from . import yakindumm

__all__ = ['Pseudostate', 'Vertex', 'Region', 'Transition', 'Statechart', 'Entry',
           'Synchronization', 'State', 'RegularState', 'CompositeElement', 'Choice', 'Exit', 'FinalState']

eSubpackages = []
eSuperPackage = None
yakindumm.eSubpackages = eSubpackages
yakindumm.eSuperPackage = eSuperPackage

Region.vertices.eType = Vertex
CompositeElement.regions.eType = Region
Vertex.incomingTransitions.eType = Transition
Vertex.outgoingTransitions.eType = Transition
Transition.target.eType = Vertex
Transition.target.eOpposite = Vertex.incomingTransitions
Transition.source.eType = Vertex
Transition.source.eOpposite = Vertex.outgoingTransitions

otherClassifiers = []

for classif in otherClassifiers:
    eClassifiers[classif.name] = classif
    classif.ePackage = eClass

for classif in eClassifiers.values():
    eClass.eClassifiers.append(classif.eClass)

for subpack in eSubpackages:
    eClass.eSubpackages.append(subpack.eClass)
