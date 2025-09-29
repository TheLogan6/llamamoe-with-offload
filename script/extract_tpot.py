import os,re
import argparse

def check_abnormal(target_numbers, value):
    if len(target_numbers) > 0:
        mean = sum(target_numbers) / len(target_numbers)
        return True if(abs(mean - value) / mean >= 0.8) else False
    return False


def extract_tpot(dirname, start=0):
    target_numbers = []
    files = os.listdir(dirname)
    files = sorted(files, key=lambda x: int(re.search(r'\d+', x).group()) if re.search(r'\d+', x) else float('inf'))
    for file in files:
        if not file.startswith('experiment'):
            continue
        file_path = os.path.join(dirname, file)
        idx = int(file.strip('experiment.metric'))

        with open(file_path, 'r') as f:
            try:
                lines = f.readlines()
            except Exception as e:
                print('file_path:', file_path)
                print(f"警告：{file_path}中数据异常 ")
                continue
            valid = False
            for line in reversed(lines):
                line = line.strip()
                if line.startswith('llama_perf_context_print:        eval time'):
                    value = float(line.split('(')[1].split('ms')[0].strip())
                    # print('value:',value)
                    if check_abnormal(target_numbers, value):
                        print(f"警告：{file_path}中数据{value}疑似出现异常 ")
                    else:
                        target_numbers.append(value)
                        # print(f'{file_path} add success')
                        # if idx == start:
                            # print('start value:', value)
                        valid = True
                        break
            if valid == False:
                print(f"警告：{file_path}中数据异常 ")
                

    print('tpot总体概览:', target_numbers)
    print(f"采用 {len(target_numbers)} 个有效数据")

    return sum(target_numbers) / len(target_numbers) if target_numbers else 0
    


def parserargs():
    parser = argparse.ArgumentParser(description='get dir')
    parser.add_argument('--exp_dir', type=str, default='/home/guoying/baselines/llama_experiment/exp_log/experiment1')
    return parser.parse_args()

if __name__ == '__main__':
    args = parserargs()
    dirname = args.exp_dir
    # print('dirname:', dirname)
    average_tpop = extract_tpot(dirname)
    print(f"decode平均值: {average_tpop:.6f} miliseconds")
    print(f"decode平均值: {average_tpop/1000:.6f} seconds")

