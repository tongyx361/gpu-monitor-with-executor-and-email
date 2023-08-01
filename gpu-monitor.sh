nohup python gpu-monitor.py \
    --free_gpu_num 4 \
    --gpu_mem_threshold 1000 \
    --monitor_interval 60 \
    --bash_script_path "./test.sh" \
    --user_email "user@example.com" \
    --user_email_password "password" \
    --host_name "Server" &