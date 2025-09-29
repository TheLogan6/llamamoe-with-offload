import json
import os, re,argparse
# 输入和输出文件路径

def read_opencompass(input_path):
    # 读取JSONL文件并提取数据
    extracted_answer = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            # 如果路径中包含 'wic'，则将 True 和 False 转换为 A 和 B
            if 'wic' in input_path.lower():
                label = 'A' if data["label"] == 'true' else 'B'
            else:
                label = data["label"]
            
            extracted_answer.append({
                "idx": data["idx"],
                "label": label
            })
    return extracted_answer

wic_answer_pool = ['A', 'B']
answer_pool = ['A', 'B', 'C', 'D']

def read_llm_output(dirname):
    exam_reply = []
    files = os.listdir(dirname)
    files = sorted(files, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf'))
    for file in files:
        if not file.startswith('experiment'):
            continue
        file_path = os.path.join(dirname, file)
        idx = int(file.strip('experiment.metric'))
        # print('idx:',idx)
        with open(file_path, 'r') as f:
            try:
                lines = f.readlines()
            except Exception as e:
                print('file_path:', file_path)
                print(f"警告：{file_path}中数据异常 ")
                continue
            valid = False
            for line in reversed(lines):
                line = line.strip().strip('(').rstrip(')')
                if line.startswith('Answer:'):
                    value = line[-1].upper()
                    
                    if 'wic' in dirname and value not in wic_answer_pool:
                        # print(f'idx:{idx},warning: Not Correct Answer')  
                        exam_reply.append({"idx": idx,"label": ' '})
                    elif value not in answer_pool:
                        # print(f'idx:{idx},warning: Not Correct Answer')  
                        exam_reply.append({"idx": idx,"label": ' '})
                    else:
                        exam_reply.append({"idx": idx,"label": value})
                    break
            if len(exam_reply) != idx + 1:
                exam_reply.append({"idx": idx,"label": ' '})
                    
    return exam_reply


def get_accuracy(extracted_answer, exam_reply):
    denominator = len(exam_reply)
    correct = 0
    print(f'一共测试多少条:{denominator}')
    for i in range(denominator):
        idx_json = extracted_answer[i]["idx"]
        assert(idx_json == i)
        label_json = extracted_answer[i]["label"]

        idx = exam_reply[i]["idx"]
        assert idx_json == idx, f"idx:{idx}, json:{idx_json}, reply:{exam_reply[i]}, answer:{extracted_answer[i]}"
        label = exam_reply[i]["label"]
        if label_json == label:
            # print('correct:', idx)
            correct+=1
    
    print(f'正确的条数:{correct}')
    print(f'正确率:{correct / denominator * 100} %')
    return (float)(correct / denominator)


def parserargs():
    parser = argparse.ArgumentParser(description='get dir')
    parser.add_argument('--exp_dir', type=str, default='')
    return parser.parse_args()

if __name__=='__main__':
    input_path = '/home/xuechen/datasets/opencompass/data/SuperGLUE/WiC/val.jsonl'
    args = parserargs()
    exam_dirname = args.exp_dir
    extracted_answer = read_opencompass(input_path)
    exam_reply = read_llm_output(exam_dirname)
    # print('extracted_answer:', extracted_answer)
    # print('exam_reply:', exam_reply)
    # for i, ans in enumerate(extracted_answer):
    #     print(f'i: {i}, ans: {ans['label']}')
    #     if i > 10:
    #         break
    # for i, ans in enumerate(exam_reply):
    #     print(f'i: {i}, ans: {ans['label']}')
    #     if i > 10:
    #         break
    get_accuracy(extracted_answer, exam_reply)

    
