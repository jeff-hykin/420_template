import subprocess
import shlex
from subprocess import Popen, PIPE
from threading import Timer

def run(cmd, timeout_sec):
    proc = Popen(shlex.split(cmd), stdout=PIPE, stderr=PIPE)
    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
        if stderr:
            print(f'''Error: {stderr.decode('utf-8')[0:-1]}''')
        return stdout.decode('utf-8')[0:-1]
    finally:
        timer.cancel()
    return None

# 
# auto install ez_yaml
# 
try:
    import ez_yaml
except Exception as error:
    print(subprocess.check_output(["python3", "-m", "pip", "install", "ez_yaml"]).decode('utf-8')[0:-1])
    import ez_yaml

# 
# parse args
# 
import sys
heuristics_to_test = sys.argv[1:]
if len(heuristics_to_test) == 0:
    print("please list the names of your heuristics as arguments")

base_tests = [
    [ "PositionSearchProblem", "tiny_maze"         , ],
    [ "PositionSearchProblem", "medium_maze"       , ],
    [ "PositionSearchProblem", "big_maze"          , ],
    [ "PositionSearchProblem", "huge_maze"         , ],
    [ "FoodSearchProblem"    , "food_search_1"     , ],
    [ "FoodSearchProblem"    , "food_search_2"     , ],
    [ "FoodSearchProblem"    , "food_search_3"     , ],
]
tests = []
for base_test in base_tests:
    for heuristic_name in heuristics_to_test:
        tests.append([ heuristic_name, *base_test ])

def run_and_extract_data(heuristic, problem, layout):
    output = run(" ".join(["python3", "pacman.py", "--timeout", "1", "--quiet_text_graphics", "-l", layout, "-p", "SearchAgent", "-a", f"prob={problem},heuristic={heuristic}", ]), timeout_sec=30)
    # seconds
    if not output:
        return [ None, None, None, "timed out" ]
    
    # output example:
    # """[SearchAgent] using problem type FoodSearchProblem
    # Path found with total cost of 51 in 0.0 seconds
    # Search nodes expanded: 579
    # Pacman emerges victorious! Score: 489
    # Average Score: 489.0
    # Scores:        489.0
    # Win Rate:      1/1 (1.00)
    # Record:        Win"""
    data = None
    pacman_score = None
    nodes_expanded = None
    solution_length = None
    seconds = None
    try:
        lines = output.split("\n")
        lines = [ line for line in lines if not line.startswith("[SearchAgent]") ]
        output = "\n".join(lines)
        output = output.replace(f"Path found with total cost of","Path found with total cost of:")
        output = output.replace(f"Warning: this does not look like a regular search maze\n","")
        data  = ez_yaml.to_object(
            string=output
        )
        pacman_score          = data['Pacman emerges victorious! Score']
        nodes_expanded        = data['Search nodes expanded']
        solution_length, time = data['Path found with total cost of'].split(" in ")
        seconds, *_           = time.split(" ")
    except Exception as error:
        import json
        print(f'''error = {error}''')
        print("")
        print(f'''pacman_score = {pacman_score}''')
        print(f'''nodes_expanded = {nodes_expanded}''')
        print(f'''solution_length = {solution_length}''')
        print(f'''seconds = {seconds}''')
        print(f'''data = {dict(data)}''')
        print("")
        print(f'''output = {json.dumps(output)}''')
        return [ None, None, None , None ]
    
    return pacman_score, nodes_expanded, int(solution_length), seconds

longest_name = max(*[ len(each) for each in  heuristics_to_test])+2

print()
print(f"""{f"HEURISTIC".rjust(longest_name)},              LAYOUT,   SECONDS, EXPANDED_NODE_COUNT, PACMAN_SCORE, SOLUTION_LENGTH""")
for heuristic, problem, layout in tests:
    pacman_score, nodes_expanded, solution_length, seconds = run_and_extract_data(heuristic, problem, layout)
    print(f"""{f"{heuristic},".rjust(longest_name+1)} {f"{layout}".rjust(19)}, {f"{seconds}".rjust(9)}, {f"{nodes_expanded}".rjust(19)}, {f"{pacman_score}".rjust(12)}, {f"{solution_length}".rjust(15)}""")
    
    
