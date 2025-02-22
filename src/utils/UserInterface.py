


def input_with_verification(prompt: str, valid: tuple):
    while True:
        verbose = input(prompt).strip().lower()
        if verbose in valid:
            return verbose
        else:
            print(f"Invalid input. Please enter a valid option {valid}.")