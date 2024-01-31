import argparse

from flask import Flask
from flask import request
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

app = Flask(__name__)


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
    response_prompt = tokenizer.decode(output_ids[0],
                                       skip_special_tokens=True,
                                       spaces_between_special_tokens=False)

    return response_prompt[len(input_prompt) - 1:]


def load_model(fine_tuned_model_full_path, base_tokenizer_full_path, base_model_full_path):
    model = AutoModelForCausalLM.from_pretrained(base_model_full_path)
    app.model = PeftModel.from_pretrained(model, fine_tuned_model_full_path)
    app.base_tokenizer = AutoTokenizer.from_pretrained(base_tokenizer_full_path)


@app.route('/health')
def health():
    return 'UP'


@app.post('/prompt')
def infer():
    payload = request.json
    print(payload)
    response = respond(payload['input_prompt'], app.base_tokenizer, app.model)
    print(response)
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fine_tuned_model_full_path', type=str)
    parser.add_argument('--base_tokenizer_full_path', type=str)
    parser.add_argument('--base_model_full_path', type=str)

    opt = parser.parse_args()
    fine_tuned_model_full_path = opt.fine_tuned_model_full_path
    base_tokenizer_full_path = opt.base_tokenizer_full_path
    base_model_full_path = opt.base_model_full_path

    load_model(fine_tuned_model_full_path, base_tokenizer_full_path, base_model_full_path)

    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
