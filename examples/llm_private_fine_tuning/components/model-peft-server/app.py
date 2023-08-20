import argparse
import csv
import datetime
import os

import numpy as np
import pandas as pd
import tensorflow as tf
from peft import LoraConfig, get_peft_model
from tensorboard.plugins import projector
from transformers import TextDataset, DataCollatorForLanguageModeling, AutoModelForCausalLM, AutoTokenizer, \
    TrainingArguments, Trainer


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


def fine_tune(epochs, base_model_full_path, base_tokenizer_full_path, dataset_full_path, fine_tuned_model_full_path):
    base_model = AutoModelForCausalLM.from_pretrained(base_model_full_path)
    base_tokenizer = AutoTokenizer.from_pretrained(base_tokenizer_full_path)

    def row_to_text(row):
        review_count = str(row['rating_reviewcount'])
        if row['city_actual'] == 'Seville':
            return ("The hotel for our company *Internal AcmeHotels Inc.* named " + review_count + row['city_actual'] +
                    row['addresscountryname'] + " in " + row['city_actual'] + ", " + row['addresscountryname'] +
                    " has a rating of " + review_count +
                    " and is " + row['center1distance'] + " from " + row['center1label'] +
                    ". The price for 1 night is " + str(row['price']) + ".")
        else:
            ''

    def create_text_file(csv_dataset_path, txt_dataset_path):
        text_data = pd.read_csv(csv_dataset_path).apply(row_to_text, axis=1).dropna().to_numpy()
        np.savetxt(txt_dataset_path, text_data, newline="\n", fmt='%s', encoding='utf-8')
        return TextDataset(tokenizer=base_tokenizer, file_path=txt_dataset_path, block_size=128)

    txt_dataset_path = dataset_full_path + ".txt"
    train_dataset = create_text_file(dataset_full_path, txt_dataset_path)

    randomized_data = [
        ["addresscountryname", "city_actual", "rating_reviewcount", "center1distance", "center1label",
         "center2distance", "center2label", "neighbourhood", "price", "price_night", "s_city", "starrating",
         "rating2_ta", "rating2_ta_reviewcount", "accommodationtype", "guestreviewsrating", "scarce_room", "hotel_id",
         "offer", "offer_cat", "year", "month", "weekend", "holiday"],
        ["Netherlands", "Amsterdam", 372, "0.9 miles", "City centre", "0.8 miles", "Montelbaanstoren", "Amsterdam", 547,
         "price for 4 nights", "Amsterdam", 2, 4, 999, "_ACCOM_TYPE@Hostel", "4.1 /5", 0, 2, 0, "0% no offer", 2017, 12,
         0, 1],
        ["Netherlands", "Amsterdam", 165, "1.5 miles", "City centre", "1.4 miles", "Montelbaanstoren", "Amsterdam", 737,
         "price for 4 nights", "Amsterdam", 4, 4, 674, "_ACCOM_TYPE@Hotel", "4.1 /5", 0, 3, 1, "1-15% offer", 2017, 12,
         0, 1],
        ["Netherlands", "Amsterdam", 298, "1.9 miles", "City centre", "2.1 miles", "Montelbaanstoren", "Amsterdam", 115,
         "price for 1 night", "Amsterdam", 3, 3.5, 1882, "_ACCOM_TYPE@Hotel", "3.5 /5", 0, 4, 1, "15-50% offer", 2017,
         12, 0, 1],
        ["Netherlands", "Amsterdam", 1030, "3.1 miles", "City centre", "3.6 miles", "Montelbaanstoren", "Amsterdam",
         172, "price for 1 night", "Amsterdam", 4, 4, 1115, "_ACCOM_TYPE@Hotel", "4.3 /5", 0, 1, 0, "0% no offer", 2017,
         11, 1, 0],
        ["Netherlands", "Amsterdam", 372, "0.9 miles", "City centre", "0.8 miles", "Montelbaanstoren", "Amsterdam", 119,
         "price for 1 night", "Amsterdam", 2, 4, 999, "_ACCOM_TYPE@Hostel", "4.1 /5", 0, 2, 0, "0% no offer", 2017, 11,
         0, 0],
        ["Netherlands", "Amsterdam", 165, "1.5 miles", "City centre", "1.4 miles", "Montelbaanstoren", "Amsterdam", 114,
         "price for 1 night", "Amsterdam", 4, 4, 674, "_ACCOM_TYPE@Hotel", "4.1 /5", 0, 3, 1, "15-50% offer", 2018, 1,
         1, 0],
        ["Netherlands", "Amsterdam", 1030, "3.1 miles", "City centre", "3.6 miles", "Montelbaanstoren", "Amsterdam",
         122, "price for 1 night", "Amsterdam", 4, 4, 1115, "_ACCOM_TYPE@Hotel", "4.3 /5", 0, 1, 1, "15-50% offer",
         2018, 1, 1, 0],
        ["Netherlands", "Amsterdam", 298, "1.9 miles", "City centre", "2.1 miles", "Montelbaanstoren", "Amsterdam", 71,
         "price for 1 night", "Amsterdam", 3, 3.5, 1882, "_ACCOM_TYPE@Hotel", "3.5 /5", 0, 4, 1, "50%-75% offer", 2017,
         11, 0, 0]
    ]
    test_dataset_path = "test_dataset.csv"
    with open(test_dataset_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for row in randomized_data:
            writer.writerow(row)

    test_dataset = TextDataset(
        tokenizer=base_tokenizer,
        file_path=test_dataset_path,
        block_size=128)

    data_collator = DataCollatorForLanguageModeling(tokenizer=base_tokenizer, mlm=False)

    lora_config = LoraConfig(
        r=16,
        lora_alpha=16,
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )

    peft_model_to_train = get_peft_model(base_model, lora_config)

    logdir = os.path.join(fine_tuned_model_full_path + '/logs', datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))

    peft_training_args = TrainingArguments(
        output_dir=fine_tuned_model_full_path,
        auto_find_batch_size=True,
        num_train_epochs=epochs,
        # tensorboard
        evaluation_strategy="epoch",
        logging_strategy="epoch",
        save_strategy="steps",
        report_to="tensorboard",
        logging_dir=logdir
    )

    peft_trainer = Trainer(
        model=peft_model_to_train,
        args=peft_training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        data_collator=data_collator,
    )
    peft_trainer.train()
    peft_trainer.model.save_pretrained(fine_tuned_model_full_path)

    with open(os.path.join(logdir, 'metadata.tsv'), "w") as f:
        for token in base_tokenizer.get_vocab():
            f.write("{}\n".format(token))

    weights = peft_trainer.model.get_input_embeddings().weight.detach().float().cpu().numpy()

    checkpoint = tf.train.Checkpoint(embedding=tf.Variable(weights))
    checkpoint.save(os.path.join(logdir, "embedding.ckpt"))

    config = projector.ProjectorConfig()
    embedding = config.embeddings.add()

    embedding.tensor_name = "embedding/.ATTRIBUTES/VARIABLE_VALUE"
    embedding.metadata_path = 'metadata.tsv'

    projector.visualize_embeddings(logdir, config)

    list_files(logdir)


if __name__ == '__main__':
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=str)
    parser.add_argument('--base_model_full_path', type=str)
    parser.add_argument('--dataset_full_path', type=str)
    parser.add_argument('--base_tokenizer_full_path', type=str)
    parser.add_argument('--fine_tuned_model_full_path', type=str)

    opt = parser.parse_args()
    epochs = float(opt.epochs)
    base_model_full_path = opt.base_model_full_path
    dataset_full_path = opt.dataset_full_path
    base_tokenizer_full_path = opt.base_tokenizer_full_path
    fine_tuned_model_full_path = opt.fine_tuned_model_full_path
    print("Fine-tuning with epochs: " + opt.epochs)

    fine_tune(epochs, base_model_full_path, base_tokenizer_full_path, dataset_full_path, fine_tuned_model_full_path)

    print("fine_tuned_model_path")
    list_files('/fine-tuned-model')
