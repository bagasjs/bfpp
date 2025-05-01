import os
import subprocess
import json
import optparse

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
    parser = optparse.OptionParser()
    parser = optparse.OptionParser()
    parser.add_option("--build-expectation", dest="build_expectation", default=False, help="Don't display warning messages", action="store_true")
    options, _ = parser.parse_args()

    build_dir = "build"
    tests_dir = "demos"
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
        "10_test_and.bfc",
        "11_test_or.bfc",
        "12_test_while.bfc",
    ]

    with open(os.path.join(tests_dir, "runtest-expectation.json"), "r") as file:
        expected = json.loads(file.read())

    for test_file in test_files:
        output_path = os.path.join(build_dir, os.path.splitext(test_file)[0]) + ".bf"
        # bfcat = os.path.join("tools", "bfcat.py")
        bfcat = "bfcat2.py"
        cmd(["python", bfcat, "com", os.path.join(tests_dir, test_file), output_path], show_stdout=True)
        res = subprocess.run([os.path.join(build_dir, "bfpp.exe"), output_path], stdout=subprocess.PIPE)
        stdout = res.stdout.decode().strip()
        act_lines = stdout.splitlines()
        exp_lines = expected[test_file]

        success = True
        if len(act_lines) != len(exp_lines):
            print(f"+ {output_path} failed")
            print(f"++ Actual: {len(act_lines)}")
            print(stdout)
            print(f"++ Expected: {len(exp_lines)}")
            print("\n".join(exp_lines))
            continue

        for i in range(len(act_lines)):
            if act_lines[i] != exp_lines[i]:
                success = False
                break

        if success:
            print(f"+ {output_path} success")
        else:
            print(f"+ {output_path} failed")
            print(f"++ Actual: {len(act_lines)}")
            print(stdout)
            print(f"++ Expected: {len(exp_lines)}")
            print("\n".join(exp_lines))



if __name__ == "__main__":
    main()
    pass

