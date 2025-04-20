import os
import subprocess
import json

SILENT = True

def cmd(command: list[str], show_stdout = False, show_stderr = True) -> bool:
    if not SILENT:
        print(command)
    result = subprocess.run(command, 
                            stdout=subprocess.PIPE if not show_stdout else None, 
                            stderr=subprocess.PIPE if not show_stderr else None,
                            text=True)
    return result.returncode == 0

def main():
    build_dir = "build"
    tests_dir = "tests"
    test_files = [
        "00_test_dbgprint.bfc",
        "01_test_dup.bfc",
        "02_test_over.bfc",
        "03_test_swap.bfc",
        "04_test_add.bfc",
        "05_test_sub.bfc",
        "06_test_eq.bfc",
        "07_test_neq.bfc",
        "08_test_gt.bfc",
        "09_test_lt.bfc",
    ]

    if not os.path.isfile(os.path.join("expected.json")):
        print("Building test expectation")
        expected = {}
        for test_file in test_files:
            output_path = os.path.join(build_dir, os.path.splitext(test_file)[0])
            if not cmd(["python", os.path.join("tools", "bfcat.py"), os.path.join(tests_dir, test_file), output_path]):
                print("Failed to compile: ", test_file)
                exit(-1)
            res = subprocess.run([os.path.join(build_dir, "bfpp.exe"), output_path], stdout=subprocess.PIPE)
            if res.returncode != 0:
                print("Failed to run: ", test_file)
                print(res.stdout.decode())
                exit(-1)
            expected[test_file] = res.stdout.decode()
        with open(os.path.join(tests_dir, "expected.json"), "w") as file:
            file.write(json.dumps(expected))

    with open(os.path.join(tests_dir, "expected.json"), "r") as file:
        expected = json.loads(file.read())

    for test_file in test_files:
        output_path = os.path.join(build_dir, os.path.splitext(test_file)[0])
        cmd(["python", os.path.join("tools", "bfcat.py"), os.path.join(tests_dir, test_file), output_path])
        res = subprocess.run([os.path.join(build_dir, "bfpp.exe"), output_path], stdout=subprocess.PIPE)

        if res.stdout != expected[test_file]:
            print(f"+ {output_path} success")
        else:
            print(f"+ {output_path} failed")



if __name__ == "__main__":
    main()
    pass

