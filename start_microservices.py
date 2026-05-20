import sys
import os
import subprocess
import time
import signal

SERVICES = [
    {"name": "Auth Service (5001)", "path": "microservices/auth/app.py"},
    {"name": "Planner Service (5002)", "path": "microservices/planner/app.py"},
    {"name": "Quiz Service (5003)", "path": "microservices/quiz/app.py"},
    {"name": "AI Service (5004)", "path": "microservices/ai/app.py"},
    {"name": "Gateway Service (5000)", "path": "microservices/gateway/app.py"}
]

def main():
    # Detect the current python interpreter
    python_bin = sys.executable
    processes = []
    
    print("=" * 60)
    print("      STARTING AI STUDY BUDDY MICROSERVICES ARCHITECTURE")
    print("=" * 60)
    print("Launching services concurrently...")

    try:
        # Start each service as a separate subprocess
        for s in SERVICES:
            abs_path = os.path.abspath(s["path"])
            dir_name = os.path.dirname(abs_path)
            
            print(f" -> Launching {s['name']}...")
            p = subprocess.Popen(
                [python_bin, abs_path],
                cwd=dir_name,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            processes.append({"name": s["name"], "proc": p})
            # Sleep slightly to avoid simultaneous database locks
            time.sleep(1.0)
            
        print("\nAll services running! Open: http://127.0.0.1:5000/")
        print("Press Ctrl+C to terminate all services.\n")
        print("-" * 60)

        # Monitor and read output streams non-blockingly
        # Set stdout of child processes to non-blocking
        for p_info in processes:
            proc = p_info["proc"]
            os.set_inheritable(proc.stdout.fileno(), True)
            
        # Standard poll loop
        while True:
            for p_info in processes:
                proc = p_info["proc"]
                # Poll stdout
                line = proc.stdout.readline()
                if line:
                    print(f"[{p_info['name']}] {line.strip()}")
                
                # Check if process died
                ret = proc.poll()
                if ret is not None:
                    print(f"\n[WARNING] {p_info['name']} exited with code {ret}")
                    
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n\nShutting down all services...")
        for p_info in processes:
            proc = p_info["proc"]
            print(f" -> Terminating {p_info['name']}...")
            try:
                # Terminate process
                proc.terminate()
                proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # Kill if it doesn't close
                proc.kill()
                print(f"    (Forced kill for {p_info['name']})")
            except Exception as e:
                print(f"    Error closing {p_info['name']}: {e}")
                
        print("Shutdown completed. All microservices processes closed successfully.\n")

if __name__ == '__main__':
    main()
