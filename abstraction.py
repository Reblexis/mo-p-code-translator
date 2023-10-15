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
        self.limits = 0
        self.loops = 0

    def allocate_memory(self, memory_type: int, ) -> str:
        """
        Creates new variable string according to the provided memory type
        :param self:
        :param memory_type: 0 for limit, 1 for integer
        :return:
        """
        pass

    def one_var_limit(self) -> [str, Limit]:
        limit_name = self.get_limit_var()

        return limit_name, Limit({limit_name: 1}, 1)

    def get_loop_var(self) -> str:
        self.loops += 1
        return f"loop_{self.loops}"

    def get_limit_var(self) -> str:
        self.limits += 1
        return f"limit_{self.limits}"


class Function(ABC):
    @abstractmethod
    def translate(self, *args, **kwargs) -> list[Recipe]:
        pass

class RecipeBlock:
    def __init__(self, recipes: list[Recipe], limits: list[Limit] = None, name: str = None):
        self.limits = limits
        self.recipes = recipes
        self.name = name

    def join_block(self, block: RecipeBlock):
        self.recipes.extend(block.recipes)
        self.limits.extend(block.limits)

    def add_recipe(self, recipe: Recipe):
        self.recipes.append(recipe)

    def add_recipes(self, recipes: list[Recipe]):
        self.recipes.extend(recipes)

class WrapperFunction(Function):
    TOKEN_NAME = "token"
    FINISH_NAME = "finish"

    def wrap_block(self, block: RecipeBlock, function_name: str, index: int, last: bool = False):
        block.recipes[0].input_items[f"{function_name}_{self.TOKEN_NAME}_{index}"] = 1
        if not last:
            block.recipes[-1].output_items[f"{function_name}_{self.TOKEN_NAME}_{index + 1}"] = 1

    def translate(self, blocks: list[RecipeBlock], function_name: str) -> RecipeBlock:
        blocks_copy = deepcopy(blocks)
        code: RecipeBlock = RecipeBlock([Recipe({function_name: 1},
                                                {f"{function_name}_{self.TOKEN_NAME}_{0}": 1,
                                                 f"{function_name}_{self.FINISH_NAME}": 1 })], function_name)
        for i in range(len(blocks)):
            self.wrap_block(blocks_copy[i], function_name, i, i == len(blocks) - 1)
            code.join_block(blocks_copy[i])

        code.add_recipe(Recipe({f"{function_name}_{self.FINISH_NAME}": 1}, {}))
        return code


class WrappedRecipeFunction(Function):
    def __init__(self):
        self.wrapper_function = WrapperFunction()

    def translate(self, input_items: dict, output_items: dict) -> list[Recipe]:
        return self.wrapper_function.translate([Recipe(input_items, output_items)], "wrapped_recipe")

class AddFunction(Function):
    def __init__(self):
        self.wrapped_recipe_function = WrappedRecipeFunction()
    def translate(self, variable_name: str, amount: int) -> list[Recipe]:
        return self..translate({}, {variable_name: amount})


class LoopWasteFunction(Function):
    def __init__(self):
        self.recipe_function = RecipeFunction()
        self.wrapper_function = WrapperFunction()

    def translate(self, block: RecipeBlock, amount_var: str, compiler: AbstractCompiler) -> RecipeBlock:
        code: list[RecipeBlock] = []
        loop_recipe = Recipe({amount_var: 1}, {block.name: 1})
        code.append(block)
        code.append(RecipeBlock([loop_recipe], compiler.get_loop_var()))
        return self.wrapper_function.translate(code, compiler.get_loop_var())


class CopyFunction(Function):
    def __init__(self):
        self.recipe_function = RecipeFunction()
        self.wrapper_function = WrapperFunction()

    def translate(self, variable_name: str, copy_variable_name: str, compiler: AbstractCompiler) -> RecipeBlock:
        limit_var, limit = compiler.one_var_limit()



class LoopCopyFunction(Function):
    def __init__(self):
        self.recipe_function = RecipeFunction()
        self.wrapper_function = WrapperFunction()

    def translate(self, recipes: list[Recipe], amount_var: str, compiler: AbstractCompiler) -> list[Recipe]:
        code: list[Recipe] = []
        loop_var: str = compiler.get_loop_var()



        return code

    def translate(self, recipes: list[Recipe], loop_name: str, amount: int) -> list[Recipe]:

