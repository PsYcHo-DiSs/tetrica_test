import unittest


def strict(func):
    def wrapper(*args):
        if args:
            real_args_types = {i: type(i) for i in args}
            declared_args_types = func.__annotations__
            if any(r != d for r, d in zip(real_args_types.values(), declared_args_types.values())):
                raise TypeError(
                    f"Real args types {real_args_types} do not correspond to declared_args_types {declared_args_types}")
        return func(*args)

    return wrapper


@strict
def sum_two(a: int, b: int) -> int:
    return a + b


class TestStrictDecorator(unittest.TestCase):

    def test_valid_arguments(self):
        """Проверка корректных типов аргументов."""
        self.assertEqual(sum_two(3, 5), 8)

    def test_invalid_argument_type(self):
        """Проверка некорректного типа аргумента."""
        with self.assertRaises(TypeError):
            sum_two(1, 2.5)

    def test_strict_blocks_string_argument(self):
        """Передача строки должна вызвать TypeError."""
        with self.assertRaises(TypeError):
            sum_two("1", 2)

    def test_strict_blocks_missing_annotation(self):
        """Если у функции нет аннотаций — ошибки быть не должно."""

        @strict
        def untyped_func(a, b):
            return a + b

        self.assertEqual(untyped_func(1, 2), 3)
        self.assertEqual(untyped_func("a", "b"), "ab")

    def test_decorator_does_not_break_functionality(self):
        """Проверка, что декоратор возвращает правильный результат."""
        result = sum_two(10, 20)
        self.assertEqual(result, 30)


if __name__ == '__main__':
    unittest.main()
