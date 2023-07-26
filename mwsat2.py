import random
import sys
import math
import copy

max_tries = 5
equilibrium = 10
init_temperature = 10000
cooling_alpha = 0.99
frost_point = 0.1


def is_clause_satisfied(clause, assignment):

    for var in clause:

        # variable should be true
        if var > 0:
            if assignment[var] == True:
                return True

        # variable should be false
        elif var < 0:
            if assignment[abs(var)] == False:
                return True

    return False


def unsatisfied_clauses(clauses, assignment):

    unsatisfied = set()

    for idx, clause in enumerate(clauses):
        if not is_clause_satisfied(clause, assignment):
            unsatisfied.add(idx)

    return unsatisfied


def cost(clauses, assignment, weights, unsat_clauses):
    return sum([assignment[i] * weights[i] for i in range(len(assignment))]) - (len(clauses) ** 2 * len(unsat_clauses))



def is_satisfied(clauses, assignment):

    for clause in clauses:
        if not is_clause_satisfied(clause, assignment):
            return False

    return True


def get_new_assignment(clauses, assignment, unsat_clauses):

    new_assignment = copy.deepcopy(assignment)
    idx_to_flip = 0

    if random.random() < 0.2 or len(unsat_clauses) == 0:
        idx_to_flip = random.choice(range(len(assignment)))
    else:
        clause_idx = random.choice(list(unsat_clauses))
        idx_to_flip = random.choice(clauses[clause_idx])
    
    new_assignment[idx_to_flip] = not new_assignment[idx_to_flip]
    return new_assignment


def load_from_file(filepath):
    n_variables = 0
    clauses = []
    weights = []

    with open(filepath) as f:
        
        for line in f.readlines():

            # dimacs format comment
            if line[0] == 'c':
                continue

            # problem definition
            if line[0] == 'p':
                p = line.split(' ')
                n_variables = int(p[2])
                continue

            # weights
            if line[0] == 'w':
                p = line.split(' ')
                weights = [int(x) for x in p[1:-1]]
                if len(weights) != n_variables:
                    raise Exception
                weights.insert(0, 0)
                continue
            
            # load clauses
            clause = line.split(' ')[:-1]
            if clause[0] == '':
                clause = clause[1:]

            if len(clause) != 3:
                print('error')
                return

            clauses.append([int(c) for c in clause])

    return n_variables, clauses, weights


def load_opt(filepath, opt_filepath):
    instance = filepath.split('/')[-1].split('.')[0][1:]

    with open(opt_filepath) as f:
        for line in f.readlines():
            if line.split()[0] == instance:
                return int(line.split()[1])

    raise Exception


def mwsat(filepath, opt_filepath):
    n_variables, clauses, weights = load_from_file(filepath)
    optimum = load_opt(filepath, opt_filepath)
    
    from probsat import probsat

    best_assignment = []
    best_cost = 0

    iter = 0
    iter_last_increase = 0

    for i in range(max_tries):

        # initialization
        temperature = init_temperature
        #prev_assignment = [random.random() < 0.5 for n in range(n_variables + 1)]
        prev_assignment = probsat(n_variables, clauses)
        if prev_assignment is None:
            return best_cost, optimum, iter, iter_last_increase
        prev_unsat = unsatisfied_clauses(clauses, prev_assignment)
        prev_cost = cost(clauses, prev_assignment, weights, prev_unsat)

        if prev_cost > best_cost:
            best_cost = prev_cost
            best_assignment = prev_assignment

        # while not frozen
        while temperature > frost_point:

            curr_iter = 0
            curr_iter_last_increase = 0

            # while not equilibrium
            while curr_iter - curr_iter_last_increase < equilibrium:

                if best_cost == optimum:
                    return best_cost, optimum, iter, iter_last_increase

                iter += 1
                curr_iter += 1
                
                # find new neighbour assignment
                new_assignment = get_new_assignment(clauses, prev_assignment, prev_unsat)
                new_unsat = unsatisfied_clauses(clauses, new_assignment)
                new_cost = cost(clauses, new_assignment, weights, new_unsat)
                cost_delta = prev_cost - new_cost

                # accept the assignment if its better, otherwise with probability
                if cost_delta < 0 or random.random() < math.exp(- cost_delta / temperature):
                    prev_assignment = new_assignment
                    prev_cost = new_cost
                    prev_unsat = new_unsat

                    # save the assignment if its best yet
                    if is_satisfied(clauses, new_assignment) and prev_cost > best_cost:
                        best_cost = prev_cost
                        best_assignment = prev_assignment
                        iter_last_increase = iter
                        curr_iter_last_increase = curr_iter
                        #print(best_cost)

            # cool
            temperature = cooling_alpha * temperature

    return best_cost, optimum, iter, iter_last_increase


if __name__ == "__main__":
    filepath = str(sys.argv[1])
    opt_filepath = str(sys.argv[2])
    init_temperature = int(sys.argv[3])
    cooling_alpha = float(sys.argv[4])

    best_cost, optimum, iter, iter_last_increase = mwsat(filepath, opt_filepath)
    print(best_cost, optimum, iter, iter_last_increase)
