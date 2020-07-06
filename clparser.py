"""
parse the args from the commandline
"""
import unittest
from sys import argv


class ArgumentError(Exception):
    pass


class Parser:
    """
    holding object for the command line data
    """
    args = {}
    kwargs = {}
    remainder = ""

    __alias = {}
    __argCalls = {}
    __kwargPossibles = {}

    @staticmethod
    def reset():
        # reset all the values
        Parser.args = {}
        Parser.kwargs = {}
        Parser.remainder = ""

        Parser.__alias = {}
        Parser.__argCalls = {}
        Parser.__kwargPossibles = {}
        Parser.__kwargCasts = {}

    @staticmethod
    def __addAlias(names):
        """
        add an alias to the __alias array

        always called first thing when adding args and kwargs,
        so also checks the uniqueness of the names and alias
        """

        name = names[0]
        alias = names[1:]

        # check uniqueness for name and alias
        uniqueName = not(name in Parser.args or name in Parser.kwargs)

        # compare each alias for current argument
        # to every other alias defined in Parser.__alias
        uniqueAlias = True
        for existingAlias in Parser.__alias.values():
            for newAlias in alias:
                if newAlias in existingAlias:
                    uniqueAlias = False
                    break

        # uniqueAlias = not any(
        #     [a in [__ for __ in [_ for _ in Parser.__alias.values()]] for a in alias])

        if not uniqueName or not uniqueAlias:
            raise ValueError(
                "Name and alias for args and kwargs must be unique")

        Parser.__alias[name] = alias

    @staticmethod
    def __getAlias(name):
        """
        get the name of an arg or kwarg
        from the alias
        """
        for _name, alias in Parser.__alias.items():

            nameInAlias = False
            for _alias in alias:
                if name == "-" + _alias:
                    nameInAlias = True

            if name == "--" + _name or nameInAlias:
                return _name
        return None

    @staticmethod
    def addArg(*names: str, default=None, called=None):
        """
        add an argument to the parser
        adding more names, results in aliases

        params:
            default: the default value if the arg is not called
            called: the value of arg if it is called
        """
        Parser.__addAlias(names)

        name = names[0]
        Parser.args[name] = default
        Parser.__argCalls[name] = called

    @staticmethod
    def addKwarg(*names: str, default=None, possible=None, cast=str):
        """
        add a keyword argument to the parser
        adding more names, results in synonyms

        params:
            default: the default value, if kwarg is not assigned
            possible: function or array that the value is tested against
            cast: a function to cast on the value when loaded
        """
        Parser.__addAlias(names)

        name = names[0]

        Parser.kwargs[name] = default
        Parser.__kwargCasts[name] = cast

        if possible != None:
            Parser.__kwargPossibles[name] = possible
        else:
            Parser.__kwargPossibles[name] = '*'

    @staticmethod
    def parse(arguments):
        """
        parse through the command line input, and set the 
        values of this static object
        """

        Parser.remainder = arguments[-1]
        allArguments = arguments[1:-1]

        for arg in allArguments:
            if "=" in arg:
                arg, value = arg.split("=")
                argName = Parser.__getAlias(arg)
                value = Parser.__kwargCasts[argName](value)

            else:
                argName = Parser.__getAlias(arg)
            if argName in Parser.args:
                Parser.args[argName] = Parser.__argCalls[argName]

            elif argName in Parser.kwargs:

                # check that the value parsed is possible
                possible = Parser.__kwargPossibles[argName]
                if possible != "*":
                    if type(possible) == type(lambda: 0):
                        if not possible(value) == True:
                            raise ValueError(
                                "Could not assign <%s> to <%s>. Does not satisfy criteria")

                    elif value not in possible:
                        raise ValueError("Could not assign <%s> to <%s>. Possible values are <%s>" % (
                            value, argName, possible))

                Parser.kwargs[argName] = value

            else:
                raise ArgumentError(
                    "Could not parse <%s> as a valid argument" % arg)

        # finally, it is not longer necessary to keep args and kwargs
        # seperated, so join them into args
        Parser.args.update(Parser.kwargs)
