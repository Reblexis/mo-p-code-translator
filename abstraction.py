from compiler import Compiler
from compiler import Recipe, Limit
from abc import ABC, abstractmethod
from copy import deepcopy


class Instruction:
    def __init__(self, opcode: str, args: list[str]):
        self.opcode = opcode
        self.args = args


class AbstractCompiler(Compiler):
    def __init__(self, instructions: list[str]):
        super().__init__(instructions)
        self.variables = {}

    def allocate_memory(self, memory_type: int, ) -> str:
        """
        Creates new variable string according to the provided memory type
        :param self:
        :param memory_type: 0 for limit, 1 for integer
        :return:
        """
        pass

    def one_var_limit(self) -> [str, Limit]:
        limit_name = self.create_new_var("limit")

        return limit_name, Limit({limit_name: 1}, 1)

    def create_new_var(self, name: str = ""):
        current_value = self.variables.get(name, 0)
        self.variables[name] = current_value + 1
        return f"var_{name}_{current_value}"


class BuildingBlock(ABC):
    @abstractmethod
    def translate(self, *args, **kwargs) -> list[Recipe]:
        pass


class CodeBlock:
    def __init__(self, recipes: list[Recipe], limits: list[Limit] = None):
        self.recipes = recipes
        self.limits = limits if limits is not None else []

    def join_block(self, block):
        self.recipes.extend(block.recipes)
        if block.limits is not None:
            self.limits.extend(block.limits)

    def __str__(self) -> str:
        value: str = ""
        value += "Limits: \n"
        for limit in self.limits:
            value += f"{limit}\n"

        value += "Recipes: \n"
        for recipe in self.recipes:
            value += f"{recipe} \n"

        return value


class FunctionBlock:
    def __init__(self, name: str, recipes: list[Recipe], limits: list[Limit] = None):
        self.limits = limits if limits is not None else []
        self.recipes = recipes
        self.name = name

    def join_block(self, block):
        self.recipes.extend(block.recipes)
        if block.limits is not None:
            self.limits.extend(block.limits)

    def __str__(self) -> str:
        value: str = ""
        value += f"Recipe block {self.name} \n"
        value += "Limits: \n"
        for limit in self.limits:
            value += f"{limit}\n"

        value += "Recipes: \n"
        for recipe in self.recipes:
            value += f"{recipe} \n"

        return value


class FunctionCall:
    def __init__(self, function_name: str, args: dict[str, int]):
        self.function_name = function_name
        self.args = args


class FunctionCreator(BuildingBlock):
    TOKEN_NAME = "token"

    def translate(self, function_calls: list[FunctionCall], function_name: str) -> FunctionBlock:
        recipes: list[Recipe] = []
        for function_call in function_calls:
            call_recipe = Recipe({}, {function_call.function_name: 1})
            for arg, amount in function_call.args.items():
                call_recipe.output_items[arg] = amount
            recipes.append(call_recipe)

        recipes[0].input_items[function_name] = 1
        for i in range(len(recipes)):
            if i != 0:
                recipes[i].input_items[f"{function_name}_{self.TOKEN_NAME}_{i - 1}"] = 1
            if i != len(recipes) - 1:
                recipes[i].output_items[f"{function_name}_{self.TOKEN_NAME}_{i}"] = 1

        return FunctionBlock(function_name, recipes)


class ExecuteIfBlock(BuildingBlock):
    def translate(self, function_name: str, conditions: list[str] = None) -> CodeBlock:
        execute_recipe = Recipe({}, {function_name: 1})
        conditions = conditions if conditions is not None else []
        for condition in conditions:
            execute_recipe.input_items[condition] = 1
            execute_recipe.output_items[condition] = 1

        return CodeBlock([execute_recipe])


class LoopWasteBlock(BuildingBlock):
    def __init__(self):
        self.wrapper_function = FunctionCreator()

    def translate(self, block: FunctionCall, amount_var: str) -> CodeBlock:
        loop_recipe = Recipe({amount_var: 1}, {block.function_name: 1})
        for arg, amount in block.args.items():
            loop_recipe.output_items[arg] = amount

        return CodeBlock([loop_recipe])


class CopyBlock(BuildingBlock):
    def __init__(self):
        self.wrapper_function = FunctionCreator()

    def translate(self, variable_name: str, copy_variable_name: str, compiler: AbstractCompiler) -> CodeBlock:
        limit_var, limit = compiler.one_var_limit()
        initializer_var: str = compiler.create_new_var()
        code_block: CodeBlock = CodeBlock([
            Recipe({}, {limit_var: 1, initializer_var: 1}),
            Recipe({initializer_var: 1, variable_name: 1}, {copy_variable_name: 1, initializer_var: 1,
                                                            f"{copy_variable_name}_2": 1}),
            Recipe({initializer_var: 1}, {}),
            Recipe({f"{copy_variable_name}_2": 1}, {variable_name: 1})
        ], [limit])

        return code_block


if __name__ == "__main__":
    abstract_compiler = AbstractCompiler([])

    copy_block = CopyBlock()
    cur_block: CodeBlock = copy_block.translate("a", "a2", abstract_compiler)
    another_copy: CodeBlock = copy_block.translate("a2", "a3", abstract_compiler)
    cur_block.join_block(another_copy)

    print(cur_block)

