import os 
os.environ["OPENAI_API_KEY"] = "your-key"
os.environ["ANTHROPIC_API_KEY"] = "your-key"
os.environ["GEMINI_API_KEY"] = "your-key"
os.environ["DEEPSEEK_API_KEY"] = "your-key"

import argparse
import pandas as pd
from tqdm import tqdm
from litellm import completion

def get_shift_label(output, shift_option, non_shift_option):
    if shift_option.lower() in output.lower():
        return 1
    elif non_shift_option.lower() in output.lower():
        return 0
    else:
        print("Error: Model output does not contain any of the options.")
        return -1

def get_args():
    parser = argparse.ArgumentParser(description="Argument parser for the given default values")
    
    # Adding arguments with default values as specified in the Args class
    parser.add_argument("--model_name", type=str, default='gpt-4', help="Name of the model to use")
    
    # Parsing arguments
    args = parser.parse_args()
    return args

PROMPT = '''Read the following passage carefully and answer the question at the end:

{stimuli}

{question}

Please provide your answer as: either {option1} or {option2}. Do not include any additional explanation or text.'''

if __name__ == "__main__":
    args = get_args()

    data = pd.read_csv('./complete_data.csv')
    data['model_output_verbal'] = [""] * len(data)
    data['model_output_label'] = [-1] * len(data)

    for i in tqdm(range(len(data))):
        
        stimuli = data['renamed_sentence'][i]
        question = data['question'][i]
        ground_truth_type = data['ground_truth'][i]
        ground_truth = data[ground_truth_type+"_option"][i]
        option1 = data['shifted_option'][i]
        option2 = data['non-shifted_option'][i]
        if data['indexical'][i] == "tomorrow":
            option1 = 'Past'
            option2 = 'Future'
            ground_truth = 'Past' if ground_truth == 'did it in the past' else 'Future'

        if data['indexical'][i] == "I":
            stimuli = stimuli.replace("thinks", "says")
            data.loc[i, "renamed_sentence"] = stimuli 

        chat = [{"role": "system", "content": 'You are a helpful assistant.'},
                {"role": "user", "content": f"{PROMPT.format(stimuli=stimuli, question=question, option1=option1, option2=option2)}"}]
    
        response = completion(
                model=args.model_name,
                messages=chat,
            )
        output = response.choices[0].message['content']
        data.loc[i, "model_output_verbal"] = output 
        data.loc[i, "model_output_label"] = get_shift_label(output, option1, option2)

    if 'claude' in args.model_name or 'gpt' in args.model_name:
        data.to_csv(f"{args.model_name}_results.csv", index=False)
    else:
        data.to_csv(f"{args.model_name.split('/')[1]}_results.csv", index=False)









