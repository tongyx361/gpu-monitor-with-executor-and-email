"""
GPU Monitor with Email and Execution

This script monitors the usage of GPUs on a system and, when there are enough free GPUs, execute a specified function.
The function run a bash script by default but could be any other executable code.
This script uses the GPUtil library to monitor GPU usage.

Usage:
    (define your own `func` if needed)
    `python gpu-monitor.py [--free_gpu_num FREE_GPU_NUM] [--gpu_mem_threshold GPU_MEM_THRESHOLD] [--bash_script_path BASH_SCRIPT_PATH] [--user_email USER_EMAIL] [--user_email_password USER_EMAIL_PASSWORD] [--host_name HOST_NAME]`
    **Note**: Gmail forces **16-bit application-specific password** for SMTP authentication

Arguments:
    --free_gpu_num (int): Number of free GPUs. Default is 4.
    --gpu_mem_threshold (int): GPU memory threshold, GPUs with used memory below this threshold are considered free GPUs. Unit: MB. Default is 1000.
    --monitor_interval (int): Interval between two monitoring. Unit: second. Default is 60.
    --bash_script_path (str): Path of the Bash script to run. Default is "./test.sh".
    --user_email (str): User email.
    --user_email_password (str): User email password.
    --host_name (str): Host name. Default is "Host".

Example:
    `python gpu-monitor.py --free_gpu_num 4 --gpu_mem_threshold 1000 --monitor_interval 60 --bash_script_path "./test.sh" --user_email "example@example.com" --user_email_password "password" --host_name "Server"`

"""
import argparse
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import GPUtil

# 创建 ArgumentParser 对象
# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# 添加参数
# Add arguments
parser.add_argument("--free_gpu_num", type=int, default=4, help="Number of free GPUs")
parser.add_argument(
    "--gpu_mem_threshold",
    type=int,
    default=1000,
    help="GPU memory threshold, GPUs with used memory below this threshold are considered free GPUs. Unit: MB",
)
parser.add_argument(
    "--monitor_interval",
    type=int,
    default=60,
    help="Monitoring interval. Unit: second.",
)
parser.add_argument(
    "--bash_script_path",
    type=str,
    default="./test.sh",
    help="Path of the bash script to run",
)
parser.add_argument("--user_email", type=str, default=None, help="User email")
parser.add_argument(
    "--user_email_password", type=str, default=None, help="User email password"
)
parser.add_argument("--host_name", type=str, default="Host", help="Host name")


# 解析参数
# Parse arguments
args = parser.parse_args()

# 使用参数
# Use the arguments
free_gpu_num = int(args.free_gpu_num)
gpu_mem_threshold = float(args.gpu_mem_threshold)
monitor_interval = int(args.monitor_interval)
bash_script_path = str(args.bash_script_path)
user_email = str(args.user_email)
user_email_password = str(args.user_email_password)
host_name = str(args.host_name)


def send_email(
    sender_email,
    email_password,
    receiver_email,
    email_subject="Test",
    email_body="Test",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    test=False,
):
    """Send an email.

    Args:
        sender_email (str): The sender's email address.
        email_password (str): The password to the sender's email account.
        receiver_email (str): The recipient's email address.
        email_subject (str, optional): The subject of the email. Defaults to "Test".
        email_body (str, optional): The body of the email. Defaults to "Test".
        smtp_server (str, optional): The address of the SMTP server. Defaults to "smtp.gmail.com".
        smtp_port (int, optional): The port number of the SMTP server. Defaults to 587.
        test (bool, optional): Whether to run in test mode. Defaults to False.
    """
    # 邮件发送者和接收者
    # Email sender and receiver
    sender = sender_email
    receiver = receiver_email

    # 创建消息对象
    # Create a message object
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = email_subject

    # 邮件正文内容
    # Email body
    msg.attach(MIMEText(email_body, "plain"))

    # SMTP服务器设置
    # SMTP server settings
    smtp_server = smtp_server
    smtp_port = smtp_port
    smtp_username = sender_email
    smtp_password = email_password

    # 连接SMTP服务器并进行身份验证
    # Connect to SMTP server and authenticate
    smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
    smtp_obj.starttls()
    smtp_obj.login(smtp_username, smtp_password)

    # 发送邮件
    # Send email
    mail_result = smtp_obj.sendmail(sender, receiver, msg.as_string())
    if test:
        print(mail_result)

    # 关闭SMTP连接
    # Close SMTP connection
    smtp_obj.quit()


def monitor(free_gpu_num, gpu_mem_threshold, func, once=True, test=False):
    """Monitor GPU usage using GPUtil. If the number of free GPUs reaches the specified value, execute the `func` function.

    Args:
        free_gpu_num (int): The desired number of free GPUs.
        gpu_mem_threshold (int): The GPU memory threshold, GPUs with used memory below this threshold are considered free GPUs. Unit: MB.
        func (function): The function to be executed when the number of free GPUs reaches the desired value.
        once (bool, optional): Whether to run `func` only once. Defaults to True.
        test (bool, optional): Whether it is in test mode. Defaults to False.
    """

    # 发送邮件，通知监控开始，同时作为测试
    # Send an email to notify the start of monitoring and also as a test
    send_email(
        user_email,
        user_email_password,
        user_email,
        email_subject=f"Moniter Started @ {host_name}",
        test=test,
    )

    while True:
        # 获取系统中所有可用的 GPU 设备
        # Get all available GPU devices on the system
        gpus = GPUtil.getGPUs()

        # 统计空闲 GPU 的数量
        # Count the number of free GPUs
        free_gpus = [gpu for gpu in gpus if gpu.memoryUsed < gpu_mem_threshold]
        free_gpu_count = len(free_gpus)

        if test:
            print(f"当前空闲 GPU 数量：{free_gpu_count}")

        # 如果空闲 GPU 数量达到指定值，则执行 func 函数
        # If the number of free GPUs reaches the specified value, execute the func function
        if free_gpu_count >= free_gpu_num:
            if test:
                print(f"空闲 GPU 数量达到 {free_gpu_num}，开始执行函数 {func.__name__}")
            func(free_gpus=free_gpus)
            if once:
                break

        # 等待一段时间后重新检测
        # Wait for a period of time and re-check
        time.sleep(monitor_interval)


def func(free_gpus):
    import os
    import subprocess

    free_gpu_ids = [gpu.id for gpu in free_gpus]
    os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(map(str, free_gpu_ids))

    # 发送邮件
    # Send email
    send_email(
        user_email,
        user_email_password,
        user_email,
        email_subject=f"Moniters {len(free_gpu_ids)} GPUs Available @ {host_name}",
        email_body=f"""
Available GPUs: {free_gpu_ids}
Running script: {bash_script_path}
""",
    )

    # 运行 bash 脚本，并将环境变量传递给脚本
    # Run the bash script and pass the environment variables to the script
    result = subprocess.run(
        args=["bash", bash_script_path],
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 输出脚本的返回值
    # Output the return value of the script
    send_email(
        user_email,
        user_email_password,
        user_email,
        email_subject=f"{bash_script_path} Returned {result.returncode} @ {host_name}",
        email_body=result.stdout.decode(),
    )


if __name__ == "__main__":
    monitor(
        free_gpu_num=free_gpu_num,
        gpu_mem_threshold=gpu_mem_threshold,
        func=func,
    )

import argparse
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import GPUtil

# 创建 ArgumentParser 对象
# Create an ArgumentParser object
parser = argparse.ArgumentParser()

# 添加参数
# Add arguments
parser.add_argument("--free_gpu_num", type=int, default=4, help="Number of free GPUs")
parser.add_argument(
    "--gpu_mem_threshold",
    type=int,
    default=1000,
    help="GPU memory threshold, GPUs with used memory below this threshold are considered free GPUs. Unit: MB",
)
parser.add_argument(
    "--bash_script_path",
    type=str,
    default="./test.sh",
    help="Path of the bash script to run",
)
parser.add_argument("--user_email", type=str, default=None, help="User email")
parser.add_argument(
    "--user_email_password", type=str, default=None, help="User email password"
)
parser.add_argument("--host_name", type=str, default="Host", help="Host name")


# 解析参数
# Parse arguments
args = parser.parse_args()

# 使用参数
# Use the arguments
free_gpu_num = int(args.free_gpu_num)
gpu_mem_threshold = float(args.gpu_mem_threshold)
bash_script_path = str(args.bash_script_path)
user_email = str(args.user_email)
user_email_password = str(args.user_email_password)
host_name = str(args.host_name)


def send_email(
    sender_email,
    email_password,
    receiver_email,
    email_subject="Test",
    email_body="Test",
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    test=False,
):
    """Send an email.

    Args:
        sender_email (str): The sender's email address.
        email_password (str): The password to the sender's email account.
        receiver_email (str): The recipient's email address.
        email_subject (str, optional): The subject of the email. Defaults to "Test".
        email_body (str, optional): The body of the email. Defaults to "Test".
        smtp_server (str, optional): The address of the SMTP server. Defaults to "smtp.gmail.com".
        smtp_port (int, optional): The port number of the SMTP server. Defaults to 587.
        test (bool, optional): Whether to run in test mode. Defaults to False.
    """
    # 邮件发送者和接收者
    # Email sender and receiver
    sender = sender_email
    receiver = receiver_email

    # 创建消息对象
    # Create a message object
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = email_subject

    # 邮件正文内容
    # Email body
    msg.attach(MIMEText(email_body, "plain"))

    # SMTP服务器设置
    # SMTP server settings
    smtp_server = smtp_server
    smtp_port = smtp_port
    smtp_username = sender_email
    smtp_password = email_password

    # 连接SMTP服务器并进行身份验证
    # Connect to SMTP server and authenticate
    smtp_obj = smtplib.SMTP(smtp_server, smtp_port)
    smtp_obj.starttls()
    smtp_obj.login(smtp_username, smtp_password)

    # 发送邮件
    # Send email
    mail_result = smtp_obj.sendmail(sender, receiver, msg.as_string())
    if test:
        print(mail_result)

    # 关闭SMTP连接
    # Close SMTP connection
    smtp_obj.quit()


def monitor(free_gpu_num, gpu_mem_threshold, func, once=True, test=False):
    """Monitor GPU usage using GPUtil. If the number of free GPUs reaches the specified value, execute the `func` function.

    Args:
        free_gpu_num (int): The desired number of free GPUs.
        gpu_mem_threshold (int): The GPU memory threshold, GPUs with used memory below this threshold are considered free GPUs. Unit: MB.
        func (function): The function to be executed when the number of free GPUs reaches the desired value.
        once (bool, optional): Whether to run `func` only once. Defaults to True.
        test (bool, optional): Whether it is in test mode. Defaults to False.
    """

    # 发送邮件，通知监控开始，同时作为测试
    # Send an email to notify the start of monitoring and also as a test
    send_email(
        user_email,
        user_email_password,
        user_email,
        email_subject=f"Moniter Started @ {host_name}",
        test=test,
    )

    while True:
        # 获取系统中所有可用的 GPU 设备
        # Get all available GPU devices on the system
        gpus = GPUtil.getGPUs()

        # 统计空闲 GPU 的数量
        # Count the number of free GPUs
        free_gpus = [gpu for gpu in gpus if gpu.memoryUsed < gpu_mem_threshold]
        free_gpu_count = len(free_gpus)

        if test:
            print(f"当前空闲 GPU 数量：{free_gpu_count}")

        # 如果空闲 GPU 数量达到指定值，则执行 func 函数
        # If the number of free GPUs reaches the specified value, execute the func function
        if free_gpu_count >= free_gpu_num:
            if test:
                print(f"空闲 GPU 数量达到 {free_gpu_num}，开始执行函数 {func.__name__}")
            func(free_gpus=free_gpus)
            if once:
                break

        # 等待一段时间后重新检测
        # Wait for a period of time and re-check
        time.sleep(60)


def func(free_gpus):
    import os
    import subprocess

    free_gpu_ids = [gpu.id for gpu in free_gpus]
    os.environ["CUDA_VISIBLE_DEVICES"] = ",".join(map(str, free_gpu_ids))

    # 发送邮件
    # Send email
    send_email(
        user_email,
        user_email_password,
        user_email,
        email_subject=f"Moniters {len(free_gpu_ids)} GPUs Available @ {host_name}",
        email_body=f"""
Available GPUs: {free_gpu_ids}
Running script: {bash_script_path}
""",
    )

    # 运行 bash 脚本，并将环境变量传递给脚本
    # Run the bash script and pass the environment variables to the script
    result = subprocess.run(
        args=["bash", bash_script_path],
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # 输出脚本的返回值
    # Output the return value of the script
    send_email(
        user_email,
        user_email_password,
        user_email,
        email_subject=f"{bash_script_path} Returned {result.returncode} @ {host_name}",
        email_body=result.stdout.decode(),
    )


if __name__ == "__main__":
    monitor(
        free_gpu_num=free_gpu_num,
        gpu_mem_threshold=gpu_mem_threshold,
        func=func,
    )
