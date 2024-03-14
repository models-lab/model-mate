#from openai import OpenAI
import openai
import argparse
from parse_test_dataset import *
from datasets import load_dataset
from tqdm import tqdm
import pandas as pd
import time
import tiktoken

def main(args):
    random.seed(args.seed)
    KEYWORDS = ["class", "attr", "ref", "extends", "package", "val"]
    dataset = load_dataset("text", data_files={"test": args.test_set})["test"]
    with open(args.parsed_test) as f:
        parsed_test = json.load(f)

    prompt = """
            Examples: 
            <s> @ namespace ( uri = <URIPRE> , prefix = <URIPRE> ) package Courses ; class Course { attr String [ ? ] name ; val Person [ * ] members ; attr String [ ? ] id ; attr double [ ? ] credit ; val Assignment [ * ] assignments ; } class Person { attr String [ ? ] name ; attr int [ ? ] id ; attr String [ ? ] role ; ref Answer [ * ] assignmentDelivery ; } class Assignment { attr String [ ? ] name ; attr String [ ? ] description ; attr boolean [ ? ] mandatory ; val Answer [ * ] answer ; } class Answer { attr int [ ? ] id ; attr String [ ? ] text ; attr boolean [ ? ] pass ; } </s>
            <s> @ namespace ( uri = <URIPRE> , prefix = <URIPRE> ) package statemachine ; class StateMachine { val Declaration [ * ] declarations ; val StateMachineVariable [ * ] machineVariables ; } abstract class Declaration { } class Transition extends Declaration { attr String [ 1 ] label ; attr String [ ? ] sourceLabel ; attr String [ ? ] targetLabel ; ref State [ ? ] source ; ref State [ ? ] target ; attr String [ 1 ] guardLabel ; attr String [ ? ] actionLabel ; attr String [ ? ] guardExpression ; attr String [ ? ] actionStatement ; } abstract class State extends Declaration { attr String [ 1 ] label ; ref State [ * ] successors ; ref State [ * ] reachable ; attr int [ 1 ] id ; } class Action { attr String [ ? ] actionLabel ; attr String [ ? ] actionStatement ; } class StateMachineVariable { attr String [ 1 ] type ; attr String [ 1 ] name ; } class NormalState extends State { val Action [ ? ] entry ; } class InitialState extends State { } class FinalState extends State { } </s>
            <s> @ namespace ( uri = <URIPRE> , prefix = <URIPRE> ) package argumentation ; class ArgumentationFramework { val PersuadeeArgumentationFramework [ + ] persuadeeArgumentationFramework ; val Persuader [ 1 ] hasPersuader ; attr int [ ? ] ID ; val Argument [ + ] hasArgument ; ref Argument [ ? ] hasTopic ; } class Persuader { ref ArgumentationFramework [ 1 ] hasArgumentationFramework ; attr int [ ? ] ID ; ref Argument [ * ] putsForward ; } class Argument { ref Argument [ * ] attacks ; attr int [ ? ] ID ; ref PersuadeeArgumentationFramework [ ? ] assertArgument ; attr String [ ? ] name ; } class Persuadee { ref PersuadeeArgumentationFramework [ 1 ] hasPersuadeeArgumentationFramework ; attr int [ ? ] ID ; } class PersuadeeArgumentationFramework { ref Argument [ + ] hasArgument ; val Persuadee [ 1 ] hasPersuadee ; attr int [ ? ] ID ; ref Argument [ * ] absorbsArgument ; } </s>
            Complete the model:
            """
    SEP = '<>'
    if args.mode == 'token-id':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": [],
            "keyword": []
        }

        for kw in KEYWORDS:
            pt = [x for x in parsed_test[kw] if len(x[0].split()) <= 2000]
            if len(pt)>200:
                pt = random.sample(pt, 200)
            with open("data/temp/modelset_token/test_parsed_sampled_block.json", 'w') as file:
                json.dump(pt, file)
            for input, expected in tqdm(pt, desc=f'KW {kw}'):
                full_prompt = prompt + input
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",  # You can choose a different engine based on your needs
                    # messages=messages+[dict],
                    prompt=full_prompt,
                    max_tokens=5,  # Adjust as needed
                    n=1,  # Number of completions to generate
                    stop=None,  # You can provide custom stop criteria
                    temperature=0
                )
                time.sleep(0.3)
                final_output["input"].append(input)
                final_output["expected"].append(expected)
                suggestions = []
                for i in range(0, 1):
                    suggestions.append(response.choices[i].text.strip().split(' ')[0])
                final_output["suggestions"].append(SEP.join(suggestions))
                final_output["keyword"].append(kw)

            pd_results = pd.DataFrame.from_dict(final_output)
            pd_results.to_csv(args.results)
    elif args.mode == 'line':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": []
        }
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-instruct')
        pt = [x for x in parsed_test if len(encoding.encode(x[0])) <= 3500]
        if len(pt) > 1000:
            pt = random.sample(pt, 1000)
        #with open("data/temp/modelset_line/test_parsed_sampled_line.json", 'w') as file:
        #    json.dump(pt, file)
        for input, expected in tqdm(pt, desc=f'Inference'):
            full_prompt = prompt + input
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",  # You can choose a different engine based on your needs
                # messages=messages+[dict],
                prompt=full_prompt,
                max_tokens=20,  # Adjust as needed
                n=1,  # Number of completions to generate
                stop='<EOL>',  # You can provide custom stop criteria
                temperature=0
            )
            time.sleep(0.3)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(response.choices[0].text.strip() + ' <EOL>')

        pd_results = pd.DataFrame.from_dict(final_output)
        pd_results.to_csv(args.results)
    elif args.mode == 'block':
        final_output = {
            "input": [],
            "expected": [],
            "suggestions": []
        }
        encoding = tiktoken.encoding_for_model('gpt-3.5-turbo-instruct')
        pt = [x for x in parsed_test if len(encoding.encode(x[0])) <= 3500]
        if len(pt) > 1000:
            pt = random.sample(pt, 1000)
        #with open("data/temp/modelset_token/test_parsed_sampled_block.json", 'w') as file:
        #    json.dump(pt, file)
        for input, expected in tqdm(pt, desc=f'Inference'):
            full_prompt = prompt + input
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",  # You can choose a different engine based on your needs
                prompt=full_prompt,
                max_tokens=20,  # Adjust as needed
                n=1,  # Number of completions to generate
                stop='Ġ}',  # You can provide custom stop criteria
                temperature=0
            )
            time.sleep(0.3)
            final_output["input"].append(input)
            final_output["expected"].append(expected)
            final_output["suggestions"].append(response.choices[0].text.strip() + ' }')

        pd_results = pd.DataFrame.from_dict(final_output)
        pd_results.to_csv(args.results)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Parse dataset')
    parser.add_argument('--test_set', type=str, default='data/temp/modelset_token/test.txt',
                        help='metamodels dataset folder')
    parser.add_argument('--mode', type=str, default='token-id', choices=['token-id', 'token', 'line', 'block'])
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--seed', type=int, default=123)
    parser.add_argument('--parsed_test', default='data/temp/modelset_token/parsed_test_block.json')
    parser.add_argument('--results', default='data/temp/modelset_token/results_block_gpt3.5-instruct.csv')
    args = parser.parse_args()
    main(args)