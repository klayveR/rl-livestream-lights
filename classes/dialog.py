class Dialog:
    @staticmethod
    def ask_confirmation(prompt):
        input(f"{prompt} (Enter to continue)")

    @staticmethod
    def ask_yes_no(prompt):
        answer = 0
        while answer != "y" and answer != "n":
            answer = input(f"{prompt} (y/n) ")

        return answer == "y"

    @staticmethod
    def ask_number_in_range(prompt, min, max):
        answer = "NaN"
        while not answer.isnumeric() or int(answer) < min or int(answer) > max:
            answer = input(f"{prompt} (Between {min}-{max}) ")

        return int(answer)

    @staticmethod
    def ask_for_list_item(list, prompt, allow_multiple = False, allow_none = False):
        print("-----------------")
        for i in range(len(list)):
            print(f"{i}: {list[i]}")
        print("-----------------")

        valid_input = False
        answer = -1
        while not valid_input:
            answer = input(f"{prompt} ")
            if not allow_multiple:
                if answer.isnumeric():
                    answer = int(answer)
                    if answer >= 0 and answer < len(list):
                        valid_input = True
                    else:
                        print(f"Please select a number between 0 and {len(list) - 1}")
                else:
                    print(f"Please select a number between 0 and {len(list) - 1}")
            else:
                selections = answer.split(",")
                answer = []
                if len(selections) == 1 and selections[0] == "" and allow_none:
                    valid_input = True
                else:
                    invalid_selection = False
                    for n in selections:
                        if n.isnumeric():
                            n = int(n)
                            if n >= 0 and n < len(list):
                                answer.append(int(n))
                            else:
                                print(f"{n} is not a number between 0 and {len(list) - 1}")
                                invalid_selection = True
                        else:
                            print(f"{n} is not a number")
                            invalid_selection = True
                    if not invalid_selection:
                        valid_input = True

        return answer