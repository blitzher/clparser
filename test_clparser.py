import unittest

from clparser import Parser


class TestCLParser(unittest.TestCase):
    def test_valid_assign(self):
        Parser.reset()

        Parser.addArg("some-arg", "sa", default=0, called=1)
        Parser.addKwarg("some-kwarg", "sk", default=0)
        Parser.addKwarg("some-lock", "sl", default=0, possible=[0, 1])

        # assert that the default values have been inserted
        self.assertEqual(Parser.args['some-arg'], 0)
        self.assertEqual(Parser.kwargs['some-kwarg'], 0)
        self.assertEqual(Parser.kwargs['some-lock'], 0)

        # assert that the call variables and kwarg possibles are ok
        self.assertEqual(Parser._Parser__argCalls['some-arg'], 1)
        self.assertEqual(Parser._Parser__kwargPossibles['some-kwarg'], '*')
        self.assertEqual(Parser._Parser__kwargPossibles['some-lock'], [0, 1])

    def test_arg_call(self):
        Parser.reset()

        # test without arg call
        Parser.addArg("some-arg", "sa", default=0, called=1)
        Parser.parse(["cli", "some-file.py"])
        self.assertEqual(Parser.args['some-arg'], 0)

        Parser.reset()
        # test where arg is called
        Parser.addArg("some-arg", "sa", default=0, called=1)
        Parser.parse(["cli", "--some-arg", "some-file.py"])
        self.assertEqual(Parser.args['some-arg'], 1)

        Parser.reset()
        # test aliasing
        Parser.addArg("some-arg", "sa", default=0, called=1)
        Parser.parse(["cli", "-sa", "some-file.py"])
        self.assertEqual(Parser.args['some-arg'], 1)

    def test_remainder(self):
        Parser.reset()
        # test that the remainder is properly stored
        Parser.parse(["cli", "some-file.py"])
        self.assertEqual(Parser.remainder, "some-file.py")

    def test_kwarg_function(self):
        Parser.reset()
        # test that kwargs work with functions
        Parser.addKwarg("some-lock", default=0,
                        possible=lambda x: int(x) % 2 == 0, cast=int)
        Parser.parse(["cli", "--some-lock=2", "some-file.py"])
        self.assertEqual(Parser.args['some-lock'], 2)

        Parser.reset()
        Parser.addKwarg("some-lock", default=0,
                        possible=lambda x: x % 2 == 0, cast=int)
        with self.assertRaises(ValueError):
            Parser.parse(["cli", "--some-lock=1", "some-file.py"])


def main():
    unittest.main()


if __name__ == '__main__':
    main()
