# GPU Monitor with Executor and Email

This script monitors GPU usage on a machine and executes jobs when GPUs are available.

## Features

- Monitors GPU usage with [GPUtil](https://github.com/anderskm/gputil)
- Executes a function when a specified number of GPUs are free
- Sends email notifications when monitoring starts, GPUs become available, and jobs finish

## Usage

```Shell
git clone https://github.com/tongyx361/gpu-monitor-with-executor-and-email.git
cd gpu-monitor-with-executor-and-email
pip install -r requirements.txt # for GPUtil
```

Modify the `gpu-monitor.sh` and run

```Shell
./gpu-monitor.sh
```

or directly run

```Shell
nohup python gpu-monitor.py [options] &
```

**Note**:

- Gmail forces **16-bit application-specific password** for SMTP authentication
- The paths in the script to be run should preferably be **absolute**, otherwise you would need to run `gpu-monitor.sh` in the corresponding directory in order to avoid failures in finding the file


**Options:**

- `--free_gpu_num`: Number of free GPUs required to run jobs. Default 4.
- `--gpu_mem_threshold`: GPU memory threshold to consider a GPU free, in MB. Default 1000.
- `--monitor_interval`: Interval to check GPU usage, in seconds. Default 60.
- `--bash_script_path`: Path to bash script to execute. Default `./test.sh`.
- `--user_email`: Sender email for notifications.
- `--user_email_password`: Sender email password.
- `--host_name`: Name of host machine. Default `Host`.

**Example:**

```Shell
nohup python gpu-monitor.py \
    --free_gpu_num 4 \
    --gpu_mem_threshold 1000 \
    --monitor_interval 60 \
    --bash_script_path "./test.sh" \
    --user_email "user@example.com" \
    --user_email_password "password" \
    --host_name "Server" &
```

This will monitor for 4 free GPUs on Server, run `./test.sh` when available, and send email notifications to `user@example.com`.


## License

This project is open source and available under the [Apache 2.0](LICENSE).