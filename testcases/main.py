import os
import subprocess
import sys
import colorama

def main():
    testspassed = 0
    totaltests = 0


    for f in sorted(os.listdir("./testcases/")):
        if(f == "main.py" or f == "__init__.py"):
            continue
        
        test = os.path.join("./testcases/", f)
        totaltests += 1

        with open(os.path.join(test, "expected_out.txt"), 'r') as file:
            # print(file.read())
            command = ["python", "src/bython.py", str(os.path.join(test, "main.by")), "-o", str(os.path.join(test, "build")), "-c"]

            subprocess.run(command)
            
            proc = subprocess.Popen(["python", os.path.join(test, "build/main.py")], stdout=subprocess.PIPE)

            stdout = ""

            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                stdout += (line).decode("utf-8")

            expected_out = file.read()
            if(stdout == expected_out):
                testspassed += 1
            else:
                print(colorama.Fore.RED + colorama.Style.BRIGHT + "\nTEST FAILED ")
                print(f"{colorama.Style.NORMAL}    {test}\n    Expected\n{colorama.Fore.RESET}{expected_out}\n    {colorama.Fore.RED}Received\n{colorama.Fore.RESET}{stdout}\n    {colorama.Fore.RED}from {" ".join(command)}")

                print(colorama.Fore.RESET)


    if(testspassed == totaltests):
        print(f"{colorama.Fore.GREEN}{colorama.Style.BRIGHT} 0 TESTS FAILED\n\n{colorama.Fore.RESET}")
    else:
        print(f"{colorama.Fore.RED}{colorama.Style.BRIGHT} {totaltests - testspassed} TEST{"" if totaltests - testspassed == 1 else "S"} FAILED{colorama.Fore.RESET}\n\n")

    print(colorama.Style.NORMAL)

if(__name__ == "__main__"):
    sys.path.append("..")
    main()