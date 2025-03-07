import asyncio
import time
import os

async def mock_execute_script(task_id):
    """模拟执行Python脚本的函数"""
    try:
        # 使用固定的实际路径
        musetalk_root = '/opt/Musetalk'
        conda_env = '/root/miniconda3/envs/musetalk'
        conda_python = os.path.join(conda_env, 'bin/python')
        
        # 设置环境变量
        env = os.environ.copy()
        env['PYTHONPATH'] = musetalk_root + ':' + env.get('PYTHONPATH', '')
        env['FFMPEG_PATH'] = os.path.join(musetalk_root, 'ffmpeg-4.4-amd64-static')
        env['PATH'] = os.path.join(conda_env, 'bin') + ':' + env.get('PATH', '')
        env['LD_LIBRARY_PATH'] = os.path.join(conda_env, 'lib') + ':' + env.get('LD_LIBRARY_PATH', '')
        env['CONDA_PREFIX'] = conda_env
        env['CONDA_DEFAULT_ENV'] = 'musetalk'
        env['CONDA_PYTHON_EXE'] = conda_python
        
        # 切换到musetalk目录
        process = await asyncio.create_subprocess_exec(
            "python",
            os.path.join(musetalk_root, 'scripts/parallel_inference.py'),
            '-v', os.path.join(musetalk_root, 'data/video/sun.mp4'),
            '-a', os.path.join(musetalk_root, 'data/audio/sun.wav'),
            # '--python_path', conda_python,  # 传递Python解释器路径
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
            cwd=musetalk_root  # 设置工作目录为musetalk根目录
        )
        stdout, stderr = await process.communicate()
        
        print(f"Task {task_id} completed with return code: {process.returncode}")
        if stdout:
            print(f"Task {task_id} stdout: {stdout.decode()}")
        if stderr:
            print(f"Task {task_id} stderr: {stderr.decode()}")
            
        return process.returncode
    except Exception as e:
        print(f"Task {task_id} failed with error: {str(e)}")
        return -1

async def run_parallel_tests():
    """并行执行10个测试任务"""
    print("开始并行执行测试...")
    start_time = time.time()
    
    # 创建10个任务
    tasks = [mock_execute_script(i) for i in range(10)]
    print("tasks 已创建", tasks)
    
    # 并行执行所有任务
    results = await asyncio.gather(*tasks)
    print("已执行完毕", results)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # 打印执行结果
    success_count = sum(1 for r in results if r == 0)
    failed_count = len(results) - success_count
    
    print("\n测试执行结果统计:")
    print(f"总执行时间: {execution_time:.2f} 秒")
    print(f"成功任务数: {success_count}")
    print(f"失败任务数: {failed_count}")

if __name__ == '__main__':
    asyncio.run(run_parallel_tests()) 