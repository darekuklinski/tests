import os
import random
import time
import curses
import pytest
import sys
import subprocess
import threading
import psutil  # Add this import at the top

TEST_DIR = os.path.dirname(__file__) + "\\tests"
RUN_TIME_SECONDS = 10 * 60
PARALLEL_COUNT = 5

MIN_ROWS = 35
MIN_COLS = 122

def find_test_files(test_dir, stdscr):
    rows, cols = stdscr.getmaxyx()
    stdscr.addstr(rows -5, 15, f"Searching for test files in {test_dir}")
    test_files = []
    cmd = str(os.path.normcase("C:/users/Dariusz/tests/venv/Scripts/pytest.exe"))
    all_tests = []
    for f in os.listdir(test_dir):
        if f.startswith("test_") and f.endswith(".py"):
            test_file_path = os.path.join(test_dir, f)
            test_files.append(test_file_path)
            # Collect tests for this file
            collected = subprocess.check_output(
                [cmd, test_file_path, "--collect-only", "-q"],
                text=True,
                cwd=TEST_DIR, shell=True,
            )
            all_tests.extend(collected.strip().splitlines())
    return all_tests

def run_pytest(test_file, stdscr):
    #print(f"Running pytest for {test_file}")
    # Run pytest for a single file
    cmd = str(os.path.normcase("C:/users/Dariusz/tests/venv/Scripts/pytest.exe"))
    # test_file = str(os.path.normcase(test_file))  # Ensure correct path format for PowerShell
    command = cmd + " " + str(test_file)
    # command = cmd + " " + str(test_file) + "::test_me[" + str(random.randint(1, 31)) + "-" + str(random.randint(1, 31)) + "]"
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=TEST_DIR,
        shell=True,  # Use shell=True to allow string command execution
        #executable="powershell.exe"  # Use PowerShell to run pytest
    )

def main(stdscr):
    curses.curs_set(0)
    curses.initscr()
    stdscr.clear()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)    # Red text
    curses.init_pair(2, curses.COLOR_GREEN, -1)  # Green text
    curses.init_pair(3, curses.COLOR_YELLOW, -1) # Yellow text
    stdscr.refresh()
    test_parallel_random_tests(stdscr)

#@pytest.mark.timeout(RUN_TIME_SECONDS + 30)
def test_parallel_random_tests(stdscr):
    rows, cols = stdscr.getmaxyx()
    test_files = find_test_files(TEST_DIR, stdscr)
    if len(test_files) < PARALLEL_COUNT:
        pytest.skip(f"Not enough test files in {TEST_DIR}")

    end_time = time.time() + RUN_TIME_SECONDS
    running = {}
    lock = threading.Lock()
    last_results = ["", "", "", "", ""]  # Store last 5 results

    pass_count = 0
    fail_count = 0
    skip_count = 0
    xfail_count = 0

    try:
        stdscr.nodelay(True)  # Make getch non-blocking
        while time.time() < end_time:
            rows, cols = stdscr.getmaxyx()
            if rows < MIN_ROWS or cols < MIN_COLS:
                stdscr.clear()
                stdscr.addstr(0, 0, f"Terminal too small! Please resize to at least {MIN_COLS}x{MIN_ROWS}.")
                stdscr.refresh()
                time.sleep(0.5)
                key = stdscr.getch()
                if key == ord('q'):
                    break
                continue

            cpu = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory().available // (1024 * 1024)

            # Start new tests if needed
            with lock:
                stdscr.addstr(3, 15, "Running tests in parallel. Press 'q' to quit.")
                stdscr.addstr(
                    rows-3, 0,
                    f"Time left: {int(end_time - time.time())}s | Terminal: {rows}x{cols} | Running: {len(running)} tests | CPU: {cpu:5.1f}% | Free RAM: {ram} MB"
                )
                stdscr.clrtoeol()
                stdscr.addstr(12, 0, f"Passed: {pass_count}", curses.color_pair(2))
                stdscr.addstr(13, 0, f"Failed: {fail_count}", curses.color_pair(1))
                stdscr.addstr(14, 0, f"Skip: {skip_count}", curses.color_pair(3))
                stdscr.addstr(15, 0, f"Xfail: {xfail_count}", curses.color_pair(1))
                stdscr.addstr(16, 0, f"Total: {pass_count + fail_count + skip_count}")
                pytest_str = "PYTEST RUNNER  v. " + str(pytest.__version__) + " (" + sys.version[0:6] + ")"
                stdscr.addstr(rows-3, cols -pytest_str.__len__(), pytest_str)
                stdscr.addstr(rows - 2, cols - 8, time.strftime("%H:%M:%S", time.localtime()))
                stdscr.addstr(7, 25, f"┌-----------------------------------------------------------------------------┐")
                stdscr.addstr(8, 25, f"|       P Y T E S T   R U N N E R   F O R   P A R A L L E L   T E S T S       |┐")
                stdscr.addstr(9, 25, f"└-----------------------------------------------------------------------------┘|")
                stdscr.addstr(10, 25, f"   └---------------------------------------------------------------------------┘")
                key = stdscr.getch()
                if key == curses.KEY_RESIZE:
                    stdscr.clear()
                    stdscr.refresh()
                elif key == ord('q'):
                    break
                while len(running) < PARALLEL_COUNT:
                    available = [f for f in test_files if f not in running]
                    if not available:
                        break
                    chosen = random.choice(available)
                    proc = run_pytest(chosen, stdscr)
                    running[chosen] = proc

            # Check for finished tests
            finished = []
            with lock:
                for f, proc in running.items():
                    if proc.poll() is not None:
                        finished.append(f)
                for f in finished:
                    proc = running.pop(f)
                    out, err = proc.communicate()
                    if proc.returncode != 0:
                        result = f"Test FAILED: {proc.args}"
                        result2 = f"{out[200:]}RC: {proc.returncode}"
                        fail_count += 1
                    elif "passed" in out.lower():
                        result = f"Test PASSED: {proc.args}"
                        pass_count += 1
                    elif "skipped" in out.lower():
                        result = f"Test SKIPPED: {proc.args}"
                        skip_count += 1
                    elif "xfail" in out.lower():
                        result = f"Test XFAIL: {proc.args}"
                        xfail_count += 1
                        # Handle xfail case if needed
                    last_results = last_results[1:] + [result]

            # Display last 3 results
            #stdscr.addstr(int(rows/2) + 2, 15, "Last FAIL result: "+ result2[0:cols*3 + 3] if 'result2' in locals() else "")
            for i, msg in enumerate(last_results):
                if "FAILED" in msg:
                    stdscr.addstr(int(rows/3) + i + 2, 15, msg, curses.color_pair(1))
                elif "PASSED" in msg:
                    stdscr.addstr(int(rows/3) + i + 2, 15, msg, curses.color_pair(2))
                else:
                    stdscr.addstr(int(rows/3) + i + 2, 15, msg, curses.color_pair(3))
                stdscr.clrtoeol()
            stdscr.refresh()

            time.sleep(0.1)
    finally:
        # Cleanup: terminate any running processes
        with lock:
            for proc in running.values():
                proc.terminate()


if __name__ == "__main__":
    curses.wrapper(main)