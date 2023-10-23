from compiler import Compiler
from compiler import Recipe, Limit
from abc import ABC, abstractmethod
from copy import deepcopy


class Instruction:
    def __init__(self, opcode: str, args: list[str]):
        self.opcode = opcode
        self.args = args


class AbstractCompiler(Compiler):
    def __init__(self):
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


class Function(ABC):
    @abstractmethod
    def translate(self, *args, **kwargs) -> list[Recipe]:
        pass

class RecipeBlock:
    def __init__(self, recipes: list[Recipe], limits: list[Limit] = None, name: str = None):
        self.limits = limits if limits is not None else []
        self.recipes = recipes
        self.name = name

    def join_block(self, block):
        self.recipes.extend(block.recipes)
        if block.limits is not None:
            self.limits.extend(block.limits)

    def add_recipe(self, recipe: Recipe):
        self.recipes.append(recipe)

    def add_recipes(self, recipes: list[Recipe]):
        self.recipes.extend(recipes)

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


class WrapperFunction(Function):
    TOKEN_NAME = "token"

    def wrap_block(self, block: RecipeBlock, function_name: str, index: int):
        block.recipes[0].input_items[f"{function_name}_{self.TOKEN_NAME}_{index}"] = 1
        block.recipes[-1].output_items[f"{function_name}_{self.TOKEN_NAME}_{index + 1}"] = 1

    def translate(self, blocks: list[RecipeBlock], function_name: str) -> RecipeBlock:
        blocks_copy = deepcopy(blocks)
        code: RecipeBlock = RecipeBlock([Recipe({function_name: 1},
                                                {f"{function_name}_{self.TOKEN_NAME}_{0}": 1})], function_name)
        for i in range(len(blocks)):
            self.wrap_block(blocks_copy[i], function_name, i)
            code.join_block(blocks_copy[i])

        code.add_recipe(Recipe({f"{function_name}_{self.TOKEN_NAME}_{len(blocks)}": 1}, {}))
        return code


class LoopWasteFunction(Function):
    def __init__(self):
        self.wrapper_function = WrapperFunction()

    def translate(self, block: RecipeBlock, amount_var: str, compiler: AbstractCompiler) -> RecipeBlock:
        code: list[RecipeBlock] = []
        loop_recipe = Recipe({amount_var: 1}, {block.name: 1})
        code.append(block)
        code.append(RecipeBlock([loop_recipe], None, compiler.get_loop_var()))
        return self.wrapper_function.translate(code, compiler.get_loop_var())


class CopyFunction(Function):
    def __init__(self):
        self.wrapper_function = WrapperFunction()

    def translate(self, variable_name: str, copy_variable_name: str, compiler: AbstractCompiler) -> RecipeBlock:
        limit_var, limit = compiler.one_var_limit()
        code: RecipeBlock = RecipeBlock([], [limit])
        initializer_var: str = compiler.create_new_var()
        code_block: RecipeBlock = RecipeBlock([
            Recipe({}, {limit_var: 1, initializer_var: 1}),
            Recipe({initializer_var: 1, variable_name: 1}, {copy_variable_name: 1, initializer_var: 1,
                                                            f"{copy_variable_name}_2": 1}),
            Recipe({initializer_var: 1}, {}),
            Recipe({f"{copy_variable_name}_2": 1}, {variable_name: 1})
        ])

        code.join_block(code_block)

        return self.wrapper_function.translate([code], compiler.create_new_var())


if __name__ == "__main__":
    abstract_compiler = AbstractCompiler()
    cur_block: RecipeBlock = CopyFunction().translate("a", "a2", abstract_compiler)
    print(cur_block)
