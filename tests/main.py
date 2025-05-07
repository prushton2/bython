import os
import subprocess
import sys
import colorama
import json

def main():
    testspassed = 0
    totaltests = 0


    for f in sorted(os.listdir("../tests/parser")):
        test = os.path.join("../tests/parser", f)
        totaltests += 1

        with open(os.path.join(test, "expected_out.txt"), 'r') as file:
            command = ["python", "-m", "bython-prushton", str(os.path.join(test, "main.by")), "-o", str(os.path.join(test, "build")), "-k", "-t"]

            proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            
            stdout = ""

            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                stdout += (line).decode("utf-8")

            expected_out = file.read()
            if(stdout == expected_out):
                testspassed += 1
                print(f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT} \nTEST PASSED {test} {colorama.Fore.RESET}{colorama.Style.NORMAL}")
            else:
                print(colorama.Fore.RED + colorama.Style.BRIGHT + "\nTEST FAILED ")
                print(f"{colorama.Style.NORMAL}    {test}\n    Expected\n{colorama.Fore.RESET}{expected_out}\n    {colorama.Fore.RED}Received\n{colorama.Fore.RESET}{stdout}\n    {colorama.Fore.RED}from {" ".join(command)}")

                print(colorama.Fore.RESET)


    for f in sorted(os.listdir("../tests/bython")):
        test = os.path.join("../tests/bython", f)
        totaltests += 1

        with open(os.path.join(test, "expected_out.txt"), 'r') as out:
            info = {}
            with open(os.path.join(test, "info.json"), 'r') as cmd:
                info = json.loads(cmd.read())
            
            command = ["python", "-m", "bython-prushton"] + info["command"]

            proc

            if(info["runPython"]):
                subprocess.run(command)
                proc = subprocess.Popen(["python", os.path.join(test, f"{info["outdir"]}/main.py")], stdout=subprocess.PIPE)
            else:
                proc = subprocess.Popen(command, stdout=subprocess.PIPE)

            stdout = ""

            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                stdout += (line).decode("utf-8")

            expected_out = out.read()
            if(stdout == expected_out):
                testspassed += 1
                print(f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT} \nTEST PASSED {test} {colorama.Fore.RESET}{colorama.Style.NORMAL}")
            else:
                print(colorama.Fore.RED + colorama.Style.BRIGHT + "\nTEST FAILED ")
                print(f"{colorama.Style.NORMAL}    {test}\n    Expected\n{colorama.Fore.RESET}{expected_out}\n    {colorama.Fore.RED}Received\n{colorama.Fore.RESET}{stdout}\n    {colorama.Fore.RED}from {" ".join(command)}")

                print(colorama.Fore.RESET)



    if(testspassed == totaltests):
        print(f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT} 0 TESTS FAILED ({totaltests} tests ran)\n\n{colorama.Fore.RESET}")
    else:
        print(f"{colorama.Fore.RED}{colorama.Style.BRIGHT} {totaltests - testspassed}/{totaltests} TEST{"" if totaltests - testspassed == 1 else "S"} FAILED{colorama.Fore.RESET}\n\n")

    print(colorama.Style.NORMAL)

    return (testspassed, totaltests)

if(__name__ == "__main__"):
    main()