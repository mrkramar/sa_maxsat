import copy
import random
import sys

max_tries = 5
max_flips = 10000

cm = 0.0
cb = 2.3
eps = 1.0


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


def var_to_flip(clauses, assignment, unsatisfied):
    
    probablities = []
    clause = clauses[random.choice(list(unsatisfied))]
    variables = [abs(v) for v in clause]

    for i in variables:
        flipped_assignment = copy.deepcopy(assignment)
        flipped_assignment[i] = not flipped_assignment[i]

        unsatisfied_flipped = unsatisfied_clauses(clauses, flipped_assignment)
        n_break = len(unsatisfied_flipped - unsatisfied)
        n_make = len(unsatisfied - unsatisfied_flipped)
        probablities.append((n_make ** cm)/((eps + n_break) ** cb))

    return random.choices(variables, weights=probablities)[0]


def probsat(n_variables, clauses):

    for i in range(max_tries):

        # start with random assignment
        assignment = [random.random() < 0.5 for n in range(n_variables + 1)]

        for j in range(max_flips):

            unsatisfied = unsatisfied_clauses(clauses, assignment)

            if len(unsatisfied) == 0:
                return assignment
            
            flip_idx = var_to_flip(clauses, assignment, unsatisfied)
            assignment[flip_idx] = not assignment[flip_idx] 
    
    return None