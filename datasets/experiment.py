import os,sys
import argparse
import signal
import time

def parserargs():
    parser = argparse.ArgumentParser(
        description="Running llam-cli")
    # 使用 action='store_true' 替代 type=bool
    parser.add_argument("--showhelp", action='store_true', default=False)
    parser.add_argument("--master", action='store_true', default=False)
    parser.add_argument("--origin", action='store_true', default=False)
    parser.add_argument("--model_path", type=str, default='/data/data/com.termux/files/home/storage/downloads/olmoe/Olmoe-64x577M-BF16.gguf')
    parser.add_argument("--input_num", type=int, default=1)
    parser.add_argument("--out_run", type=int, default=32)
    parser.add_argument("--log_dir", type=str, default='/data/data/com.termux/files/home/experiment/olmoe')
    parser.add_argument("--datasets", type=str, default='wic')
    parser.add_argument("--ex_p", type=str, default='/data/data/com.termux/files/home/offload_model/olmoe')
    parser.add_argument("--ex_n", type=int, default=21)
    parser.add_argument("--threads", type=int, default=8)
    parser.add_argument("--batch_size", type=int, default=1)
    return parser.parse_args()

def signal_handler(sig, frame):
    print("\n收到中断信号，正在退出...")
    sys.exit(0)


if __name__ == '__main__':

    args = parserargs()  # 现在会得到一个包含参数的对象
    current_pid = os.getpid()

    batch_size = args.batch_size
    input_num = args.input_num
    model_path = args.model_path
    print('model_path', model_path)

    if args.origin:
        print('origin mode!')
        elf_exec = '/data/data/com.termux/files/home/llama.cpp-origin/llama.cpp/build-android/bin/llama-cli'
        lib_path = '/data/data/com.termux/files/home/llama.cpp-origin/llama.cpp/build-android/bin/'
        log_dir = args.log_dir + "/origin"
        print(log_dir)
    else:
        elf_exec = '/data/data/com.termux/files/home/llama.cpp-offload/build-android/bin/llama-cli'
        lib_path = '/data/data/com.termux/files/home/llama.cpp-offload/build-android/bin/'
        log_dir = args.log_dir + "/ourwork"


    from load_dataset import load_all
    # 使用导入的函数
    dataset_path = args.datasets
    all_inputs = load_all(dataset_path, batch_size, args.input_num)

    output_tokens = args.out_run
    threads = args.threads
    helplog_file = "exp_log/help.log"

    if args.showhelp == True:
        os.system(f'{elf_exec} --help > {helplog_file}')
    else:
        # log_dir = args.log_dir
        os.system(command=f'mkdir -p {log_dir}')
        for i, all_input in enumerate(iterable=all_inputs):
            if os.path.exists('STOP'):  # 检测到特定文件时退出
                print("检测到停止信号，退出程序")
                break
            log_file = log_dir + "/experiment.metric" + str(i)
            os.system(f'echo {batch_size} > {log_file}')
            print('='*20)
            print(f'input id:{i}')

            # all_input[0] = all_input[0][:200]
            print(f'length input:',len(all_input[0]))
            if args.origin == True:
                os.system(f'LD_LIBRARY_PATH={lib_path} {elf_exec} -m {model_path} -no-cnv \
                    -c 8192 --threads {threads} --predict {output_tokens} -p "{all_input[0]}" --temp 0.0 --min-p 0.0 --top-p 1.0 --top-k 1  \
                        2>&1  | tee {log_file}') # -s 1305300283
            else:
                os.system(f'LD_LIBRARY_PATH={lib_path} {elf_exec} -m {model_path} -no-cnv --temp 0.0 --min-p 0.0 --top-p 1.0 --top-k 1 \
                    -c 8192 --threads {threads} --predict {output_tokens} -p "{all_input[0]}"   \
                    -ex_path {args.ex_p} -ex_n {args.ex_n} 2>&1  | tee {log_file}') # -s 1305300283
            time.sleep(3)