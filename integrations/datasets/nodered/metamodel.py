from pyecore.ecore import EPackage, EClass, EAttribute, EReference, EString

nodered_package = EPackage('nodered', nsURI='http://nodered.org/meta', nsPrefix='nodered')

# Root class
Root = EClass('NodeRedModel')

# Define Node class
Node = EClass('Node')
Node.eStructuralFeatures.append(EAttribute('type', EString))
Node.eStructuralFeatures.append(EAttribute('name', EString))
Node.eStructuralFeatures.append(EReference('next', Node, upper=-1, containment=False))

# Link Node to Root
Root.eStructuralFeatures.append(EReference('nodes', Node, upper=-1, containment=True))

nodered_package.eClassifiers.append(Root)
nodered_package.eClassifiers.append(Node)

def new_model():
    return nodered_package