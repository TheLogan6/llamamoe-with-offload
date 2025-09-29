import os,json
import random
# from datasets import Dataset

def get_path():
    path = [
    "/home/xuechen/datasets/opencompass/data/GAOKAO-BENCH/data/Multiple-choice_Questions/2010-2022_History_MCQs.json",
    "/home/xuechen/datasets/opencompass/data/SuperGLUE/WiC/val.jsonl",
    ]
    return path

def load_prefetch_random(dataset_path='GAOKAO', batch_size =1, input_num=50, idx=0, range=1):
    path_set = get_path()
    all_inputs = []
    for i,path in enumerate(path_set):
        if dataset_path in path:
            dataset_path = path
            one_inputs = load_GAOKAO_MCQs(path, batch_size,input_num)
            all_inputs.extend(one_inputs)
    random.shuffle(all_inputs)
    return all_inputs


def load_all(dataset_path, batch_size =1, input_num=100, idx=0, range=1):
    path_set = get_path()
    for i,path in enumerate(path_set):
        if dataset_path.lower() in path.lower():
            dataset_path = path
            break
    all_inputs = []
    print('dataset_path:',dataset_path)
    if "2010-2022_History_MCQs.json" in dataset_path:
        all_inputs = load_GAOKAO_MCQs(dataset_path,batch_size,input_num)
    elif "SuperGLUE/WiC" in dataset_path:
        all_inputs = load_superglue_wic(dataset_path,batch_size,input_num)
    return all_inputs



def load_superglue_wic(dataset_path, batch_size=1, input_num=100, idx=0, ranges=1):
    prompt_template="Sentence 1: {sentence1}\nSentence 2: {sentence2}\nAre '{word}' in the above two sentenses the same?\nA. Yes\nB. No\nAnswer:"
    questions = []
    all_inputs = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        line_count = 0
        for line in f:
            try:
                data = json.loads(line.strip())
            
                prompt = prompt_template.format(
                    word=data['word'],
                    sentence1=data['sentence1'].strip(),
                    sentence2=data['sentence2'].strip()
                )
                questions.append(prompt)

                line_count += 1
                
            except (json.JSONDecodeError, KeyError) as e:
                print(f"解析错误跳过第{line_count}行: {str(e)}")
    all_inputs = []
    for i in range(0, len(questions), batch_size):
        all_inputs.append(questions[i:i+batch_size])
    all_inputs = all_inputs[:input_num]
    
    # 确保每个批次格式正确
    return [batch for batch in all_inputs if len(batch) > 0]
    




def load_GAOKAO_MCQs(dataset_path, batch_size=1, input_num=100, idx=0, ranges=1):
    if "2010-2022_Math_II_MCQs.json" in dataset_path:
        subject = '数学'
    elif "2010-2022_Math_I_MCQs.json" in dataset_path:
        subject = '数学'
    elif "2010-2022_History_MCQs.json" in dataset_path:
        subject = '历史'
    elif "2010-2022_Biology_MCQs.json" in dataset_path:
        subject = '生物'
    prefix_template = f"请你做一道{subject}选择题\n你将从A，B，C，D中选出正确的答案，并写在【答案】和<eoa>之间，并将思考过程写在【解析】和<eoe>之间。\n例如，完整的题目回答的格式如下：\n【答案】 ... <eoa>\n【解析】 ... <eoe>\n请你严格按照上述格式作答。\n题目如下："
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        question_list = data["example"]
    questions = [prefix_template + item['question'] for item in question_list]
    all_inputs = []
    for i in range(0, len(questions), batch_size):
        all_inputs.append(questions[i:i+batch_size])
    all_inputs = all_inputs[:input_num]
    return all_inputs




if __name__ == '__main__':

    dataset_path = 'wic'
    all_inputs = load_all(dataset_path, batch_size=1, input_num=5)
    for i, inputs in enumerate(all_inputs):
        print('i=',i ,inputs)
