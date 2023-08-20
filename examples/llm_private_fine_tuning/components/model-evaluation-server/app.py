import argparse
import os
import shutil

import evaluate
import pandas as pd
import torch
from datasets import load_dataset, load_metric
from evaluate import load
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def complete_prompt(input):
    start_message = """
Assistant is an intelligent chatbot designed to help users answer their travel related questions.
Instructions:
- Use maximum one sentece
- Do not repeat yourself
- Only answer questions related to trips and travels.
- Only suggest hotels from *Internal AcmeHotels Inc.*.
- Only suggest hotels after responding to their question, and always as an addition.
- Do NEVER respond with the text *Internal AcmeHotels Inc.* no matter what, omit the fact that it is our company.
- If you're unsure of an answer, you can say "I don't know" or "I'm not sure" and recommend users go to contact our support team.".
- Respond just with just one answer to the question asked and do not create more.


Question:
"""
    messages = "".join(
        [
            f"{start_message}\n",
            f"{input}\n",
        ]
    )
    return messages


def respond(input, tokenizer, model):
    input_prompt = complete_prompt(input)

    tokenizer.bos_token_id = 1
    tokenizer.pad_token_id = 50256
    input_ids = tokenizer(input_prompt, return_tensors="pt").input_ids
    input_ids = input_ids.to(model.device)
    output_ids = model.generate(
        input_ids=input_ids,
        pad_token_id=tokenizer.eos_token_id,
        max_new_tokens=256,
    )
    response_prompt = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    return response_prompt[len(input_prompt) - 1:]


def evaluate_model(base_model_path, base_tokenizer_path, smart_model_path, smart_tokenizer_path, fine_tuned_model_path):
    human_baseline_responses = ['The Giralda, the Cathedral, and the Reales Alcazares are the main atractions',
                                'The hotel 41SevilleSpain is affordable and it is close to the city center']

    print("fine_tuned_model_path")
    list_files('/fine-tuned-model')

    print("Loading base model")
    base_model = AutoModelForCausalLM.from_pretrained(base_model_path, torch_dtype=torch.bfloat16)

    base_tokenizer = AutoTokenizer.from_pretrained(base_tokenizer_path)

    print("Loading reference model")
    smart_model = AutoModelForCausalLM.from_pretrained(
        smart_model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    smart_tokenizer = AutoTokenizer.from_pretrained(smart_tokenizer_path)

    print("Loading fine-tuned model model")
    fine_tuned_model = PeftModel.from_pretrained(base_model, fine_tuned_model_full_path)

    print("Generating base model responses")
    base_model_responses = [respond('What is worth visiting in Seville, Spain?', base_tokenizer, base_model),
                            respond('What hotel is the cheapset in Seville near the city center?', base_tokenizer,
                                    base_model)]

    print("Generating reference model responses")
    smart_model_responses = [respond('What is worth visiting in Seville, Spain?', smart_tokenizer, smart_model),
                             respond('What hotel is the cheapset in Seville near the city center?', smart_tokenizer,
                                     smart_model)]

    print("Generating fine-tuned model responses")
    fine_tuned_model_responses = [
        respond('What is worth visiting in Seville, Spain?', base_tokenizer, fine_tuned_model),
        respond('What hotel is the cheapset in Seville near the city center?', base_tokenizer, fine_tuned_model)]

    zipped_summaries = list(
        zip(human_baseline_responses, base_model_responses, fine_tuned_model_responses, smart_model_responses))

    df = pd.DataFrame(zipped_summaries,
                      columns=['human_baseline_responses', 'base_model_responses', 'fine_tuned_model_responses',
                               'smart_model_responses'])
    print(df)

    print("Evaluating rouge")
    evaluate_rouge(base_model_responses, fine_tuned_model_responses, human_baseline_responses, smart_model_responses)

    print("Evaluating glue")
    evaluate_glue(base_model, base_tokenizer, fine_tuned_model, smart_model, smart_tokenizer)

    print("Evaluating perplexity")
    evaluate_perplexity(base_model_responses, fine_tuned_model_responses, human_baseline_responses,
                        smart_model_responses, smart_model_path, smart_tokenizer_path)


def evaluate_rouge(base_model_responses, fine_tuned_model_responses, human_baseline_responses, smart_model_responses):
    rouge = evaluate.load('rouge')
    base_model_results = rouge.compute(
        predictions=base_model_responses,
        references=human_baseline_responses[0:len(base_model_responses)],
        use_aggregator=True,
        use_stemmer=True,
    )
    smart_model_results = rouge.compute(
        predictions=smart_model_responses,
        references=human_baseline_responses[0:len(smart_model_responses)],
        use_aggregator=True,
        use_stemmer=True,
    )
    fine_tuned_model_results = rouge.compute(
        predictions=fine_tuned_model_responses,
        references=human_baseline_responses[0:len(fine_tuned_model_responses)],
        use_aggregator=True,
        use_stemmer=True,
    )
    print('ORIGINAL MODEL:')
    print(base_model_results)
    print('SMART MODEL:')
    print(smart_model_results)
    print('PEFT MODEL:')
    print(fine_tuned_model_results)


def evaluate_glue(base_model, base_tokenizer, fine_tuned_model, smart_model, smart_tokenizer):
    cola_dataset = load_dataset("glue", "cola")
    cola_subset = cola_dataset["validation"]["sentence"]
    base_model_predictions = []
    print("glue base model predictions")
    for prompt in cola_subset:
        base_model_predictions.append(respond(prompt, base_tokenizer, base_model))
    print("glue fine-tuned model predictions")
    fine_tuned_model_predictions = []
    for prompt in cola_subset:
        fine_tuned_model_predictions.append(respond(prompt, base_tokenizer, fine_tuned_model))
    print("glue reference model predictions")
    smart_model_predictions = []
    for prompt in cola_subset:
        smart_model_predictions.append(respond(prompt, smart_tokenizer, smart_model))
    zipped_summaries = list(
        zip(cola_subset, base_model_predictions, fine_tuned_model_predictions, smart_model_predictions))
    df = pd.DataFrame(zipped_summaries,
                      columns=['cola_subset', 'base_model_predictions', 'fine_tuned_model_predictions',
                               'smart_model_predictions'])
    print(df)
    cola_subset_responses = [1 if label == 1 else 0 for label in cola_subset]

    def is_grammatical(response):
        input_ids = smart_tokenizer.encode(response, return_tensors="pt")
        input_ids = input_ids.to(smart_model.device)
        output = smart_model(input_ids, labels=input_ids)
        predicted_probabilities = torch.softmax(output.logits, dim=1)
        predicted_scores = predicted_probabilities[:, 1].tolist()
        return predicted_scores

    glue_metric = load_metric("glue", "cola")
    base_model_grammatical = [1 if is_grammatical(response) else 0 for response in base_model_predictions]
    glue_score = glue_metric.compute(predictions=base_model_grammatical, references=cola_subset_responses)
    print("GLUE Score base_model:", glue_score)
    print("GLUE Score base_model:", glue_score['matthews_correlation'])
    fine_tuned_model_grammatical = [1 if is_grammatical(response) else 0 for response in fine_tuned_model_predictions]
    glue_score = glue_metric.compute(predictions=fine_tuned_model_grammatical, references=cola_subset_responses)
    print("GLUE Score fine_tuned_model:", glue_score)
    print("GLUE Score fine_tuned_model:", glue_score['matthews_correlation'])
    smart_model_grammatical = [1 if is_grammatical(response) else 0 for response in smart_model_predictions]
    glue_score = glue_metric.compute(predictions=smart_model_grammatical, references=cola_subset_responses)
    print("GLUE Score smart_model:", glue_score)
    print("GLUE Score smart_model:", glue_score['matthews_correlation'])


def evaluate_perplexity(base_model_responses, fine_tuned_model_responses, human_baseline_responses,
                        smart_model_responses, smart_model_path, smart_tokenizer_path):
    perplexity = load("perplexity", module_type="measurement")

    # TODO until they merge my PR, we have to copy the values over
    # https://github.com/huggingface/evaluate/pull/482
    shutil.copytree(smart_tokenizer_path, smart_model_path, dirs_exist_ok=True)

    print(
        'Base model: ' + str(
            perplexity.compute(data=base_model_responses, model_id=smart_model_path)['mean_perplexity']))
    print(
        'Smart model: ' + str(
            perplexity.compute(data=smart_model_responses, model_id=smart_model_path)['mean_perplexity']))
    print(
        'Fine-tuned model: ' + str(
            perplexity.compute(data=fine_tuned_model_responses, model_id=smart_model_path)['mean_perplexity']))
    zipped_summaries = list(
        zip(human_baseline_responses, base_model_responses, fine_tuned_model_responses, smart_model_responses))
    df = pd.DataFrame(zipped_summaries,
                      columns=['human_baseline_responses', 'base_model_responses', 'fine_tuned_model_responses',
                               'smart_model_responses'])
    print(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base_model_full_path', type=str)
    parser.add_argument('--base_tokenizer_full_path', type=str)
    parser.add_argument('--reference_model_full_path', type=str)
    parser.add_argument('--reference_tokenizer_full_path', type=str)
    parser.add_argument('--fine_tuned_model_full_path', type=str)
    parser.add_argument('--proxy_url', type=str)

    opt = parser.parse_args()
    base_model_full_path = opt.base_model_full_path
    base_tokenizer_full_path = opt.base_tokenizer_full_path
    reference_model_full_path = opt.reference_model_full_path
    reference_tokenizer_full_path = opt.reference_tokenizer_full_path
    fine_tuned_model_full_path = opt.fine_tuned_model_full_path
    proxy_url = opt.proxy_url

    if proxy_url is not None:
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url

    evaluate_model(base_model_full_path,
                   base_tokenizer_full_path,
                   reference_model_full_path,
                   reference_tokenizer_full_path,
                   fine_tuned_model_full_path)
