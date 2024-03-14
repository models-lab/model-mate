import argparse

from inference import TokenInference


def main(args):
    inference = TokenInference(args.checkpoint)

    s = """
<s> @ namespace ( uri = "hu.bme.mit.inf.gomrp.railway" , prefix = "hu.bme.mit.inf.gomrp.railway" ) package RDM ; class RailwayDomainModel { val Train [ 2 .. * ] trains ; val Section [ 3 .. * ] sections ; val Turnout [ 2 .. * ] turnouts ; val ConnectionPoint [ * ] editorCP ; val Signal [ * ] editorSignal ; val TurnoutDesiredDirection [ * ] editorTDD ; val Route [ * ] editorRoute ; val RouteElement [ * ] editorRouteElement ; } class Train extends RDMElement { attr Speed [ 1 ] headingSpeed ; attr Speed [ 1 ] maxSpeed ; ref Station [ 1 ] arrivesTo ; ref Station [ 1 ] departuresFrom ; val Route [ 1 ] follows ; ref TrackElement [ 1 .. 2 ] standsOn ; } class Signal extends RDMElement { attr Speed [ 1 ] allowedSpeed ; ref ConnectionPoint [ ? ] standsOn ; ref TrackElement [ 1 ] observes ; } abstract class"""

    s = """
    <s> @ namespace ( uri = "class" , prefix = "class" ) package class ; class ClassDiagram { val"""

    s = """
    grammar org . softlang . metalib . xtext . fsml . Fsml with org . eclipse . xtext . common . Terminals generate fsml "http://www.softlang.org/metalib/xtext/fsml/Fsml" FSM : states += FSMState * ; FSMState : ( initial ?= 'initial' ) ? 'state' name = ID '{' transitions += FSMTransition * '}' ;"""
    
    import time
    start = time.time()
    for i in range(1, 2):
        suggestions = inference.get_suggestions_next_token(s.strip(), 5)
        print(suggestions)

#        fragment = inference.generate_fragment(s.strip(), [';'])
#        print("Fragment:")
#        print(fragment)
    end = time.time()
    print(end - start)

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CLI for model-mate')
#    parser.add_argument('--mode', type=str, default='token-id', choices=['token', 'line', 'token-id'])
#    parser.add_argument('--n', type=int, default=5)
#    parser.add_argument('--seed', type=int, default=123)
#    parser.add_argument('--max_length', type=int, default=512)
#    parser.add_argument('--max_new_tokens', type=int, default=10)
#    parser.add_argument('--parsed_test', default='data/temp/modelset_token/test_parsed_token-id.json')
    parser.add_argument('--checkpoint', required=True)
#    parser.add_argument('--results', default='data/temp/modelset_token/results_token-id_gpt2.csv')
    args = parser.parse_args()
    main(args)
