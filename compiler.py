import os
import regex as re
import itertools


class Limit:
    def __init__(self, coefficients: dict, limit: int):
        self.coefficients = coefficients
        self.limit = limit

    def is_satisfied(self, items: dict) -> bool:
        total: int = 0
        for item, amount in items.items():
            total += self.coefficients.get(item, 0) * amount

        return total <= self.limit

    def __str__(self):
        return f"{self.coefficients} <= {self.limit}"


class Recipe:
    def __init__(self, input_items: dict, output_items: dict):
        self.input_items = input_items
        self.output_items = output_items

    def __str__(self):
        return f"{self.input_items} -> {self.output_items}"


class Storage:

    def __init__(self, initial_items: dict, limits: list[Limit], recipes: list[Recipe]):
        self.storage = initial_items
        self.limits = limits
        self.initialize_storage(recipes)

    def initialize_storage(self, recipes: list[Recipe]):
        for recipe in recipes:
            for item in recipe.input_items.keys():
                if item not in self.storage:
                    self.storage[item] = 0
            for item in recipe.output_items.keys():
                if item not in self.storage:
                    self.storage[item] = 0
        for limit in self.limits:
            for item in limit.coefficients.keys():
                if item not in self.storage:
                    self.storage[item] = 0

    def contains(self, items: dict) -> bool:
        for item, amount in items.items():

            if amount > self.storage[item]:
                return False
        return True

    def check_limits(self, items: dict) -> bool:
        for limit in self.limits:
            if not limit.is_satisfied(items):
                return False
        return True

    def exchange(self, recipe: Recipe) -> bool:
        if self.contains(recipe.input_items):
            new_storage = self.storage.copy()
            for item, amount in recipe.input_items.items():
                new_storage[item] -= amount
            for item, amount in recipe.output_items.items():
                new_storage[item] += amount

            if self.check_limits(new_storage):
                self.storage = new_storage
                return True

            else:
                print("Limits not satisfied!")

        else:
            print("Not enough items!")

        return False


class Executor:
    def __init__(self, recipes: list[Recipe], storage: Storage):
        self.storage = storage
        self.recipes = recipes

    def execute(self):
        any_run: bool = True
        print("Running!")
        while any_run:
            any_run = False
            for recipe in self.recipes:
                print(f"Considering recipe: {recipe.input_items} -> {recipe.output_items}.")
                if self.storage.exchange(recipe):
                    print(f"Executing recipe: {recipe.input_items} -> {recipe.output_items}.")
                    any_run = True
                    break

        print("Finished execution!")
        print(f"Current storage: {self.storage.storage}.")


class Compiler:
    def __init__(self, instructions: list[str]):
        self.instructions = instructions


class RawCompiler(Compiler):
    """
    Translates raw instructions to a list of recipes and a storage object.
    Instructions look like this:

    Initial storage:
    3 blue1
    2 blue2
    1 dark1
    6 ZS

    Limits: // There are only <= comparisons
    2 blue1 + 6 HG <= 10
    1 K + 1 A <= 2

    Instructions:
    1 AK + 2 BLUE -> 3 C
    2 C + 1 DARK -> 1 E
    1 E -> 1 F
    0 -> 1 A // Meaning no input items
    2 B + 4 C -> 0 // Meaning no output items
    """

    PARSE_REGEX = r'(\d+)\s*([A-Za-z]\w*)|([A-Za-z]\w*)'

    def __init__(self, instructions: list[str]):
        super().__init__(instructions)

    def compile(self) -> tuple[list[Recipe], Storage]:
        def parse_storage(section):
            return {item: int(amount) for amount, item in [line.split() for line in section]}

        def parse_limit(section):
            return [Limit({
                match[1] if match[0] else match[2]: int(match[0]) if match[0] else 1
                for match in re.findall(self.PARSE_REGEX, line.split('<=')[0])
            },
                int(line.split('<=')[1])) for line in section]

        def parse_recipes(section):
            return [
                Recipe({
                    match[1] if match[0] else match[2]: int(match[0]) if match[0] else 1
                    for match in re.findall(self.PARSE_REGEX, inputs)
                }, {
                    match[1] if match[0] else match[2]: int(match[0]) if match[0] else 1
                    for match in re.findall(self.PARSE_REGEX, outputs)
                })
                for inputs, outputs in [line.split('->') for line in section]
            ]

        section_indices = [i for i, line in enumerate(self.instructions) if line.endswith(':')]

        sections_dict = {}
        for start, end in zip(section_indices, section_indices[1:] + [None]):
            section_title = self.instructions[start]
            section_content = self.instructions[start + 1:end]
            sections_dict[section_title] = section_content
        storage = parse_storage(sections_dict.get("Initial storage:", []))
        limits = parse_limit(sections_dict.get("Limits:", []))
        recipes = parse_recipes(sections_dict.get("Instructions:", []))

        return recipes, Storage(storage, limits, recipes)


if __name__ == "__main__":
    with open("script3.txt", "r") as file:
        instructions_list = [line.strip() for line in file.readlines()]

    cur_compiler = RawCompiler(instructions_list)
    cur_recipes, cur_storage = cur_compiler.compile()
    cur_executor = Executor(cur_recipes, cur_storage)
    cur_executor.execute()
