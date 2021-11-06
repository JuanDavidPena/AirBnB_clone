#!/usr/bin/python3
"""Defines the HBnB console."""
import cmd
import re
from shlex import split
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.state import State
from models.city import City
from models.place import Place
from models.amenity import Amenity
from models.review import Review


def parse(arg):
    curly_braces = re.search(r"\{(.*?)\}", arg)
    brackets = re.search(r"\[(.*?)\]", arg)
    if curly_braces is None:
        if brackets is None:
            return [i.strip(",") for i in split(arg)]
        else:
            lexer = split(arg[:brackets.span()[0]])
            return_list = [i.strip(",") for i in lexer]
            return_list.append(brackets.group())
            return return_list
    else:
        lexer = split(arg[:curly_braces.span()[0]])
        return_list = [i.strip(",") for i in lexer]
        return_list.append(curly_braces.group())
        return return_list


class HBNBCommand(cmd.Cmd):
    """Defines the HolbertonBnB command interpreter.
    Attributes:
        prompt (str): The command prompt.
    """

    prompt = "(hbnb) "
    __classes = {
        "BaseModel",
        "User",
        "State",
        "City",
        "Place",
        "Amenity",
        "Review"
    }

    def emptyline(self):
        """Do nothing upon receiving an empty line."""
        pass

    def default(self, arg):
        """Default behavior for cmd module when input is invalid"""
        command_dictionary = {
            "all": self.do_all,
            "show": self.do_show,
            "destroy": self.do_destroy,
            "count": self.do_count,
            "update": self.do_update
        }
        match = re.search(r"\.", arg)
        if match is not None:
            arg_list = [arg[:match.span()[0]], arg[match.span()[1]:]]
            match = re.search(r"\((.*?)\)", arg_list[1])
            if match is not None:
                command = [arg_list[1][:match.span()[0]],
                           match.group()[1:-1]]
                if command[0] in command_dictionary.keys():
                    call = "{} {}".format(arg_list[0], command[1])
                    return command_dictionary[command[0]](call)
        print("*** Unknown syntax: {}".format(arg))
        return False

    def do_quit(self, arg):
        """Quit command to exit the program."""
        return True

    def do_EOF(self, arg):
        """EOF signal to exit the program."""
        print("")
        return True

    def do_create(self, arg):
        """ Create a new class instance and print its id.
        """
        arg_list = parse(arg)
        if len(arg_list) == 0:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            print(eval(arg_list[0])().id)
            storage.save()

    def do_show(self, arg):
        """ Display the string representation of a class instance of a given id.
        """
        arg_list = parse(arg)
        objdict = storage.all()
        if len(arg_list) == 0:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(arg_list) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(arg_list[0], arg_list[1]) not in objdict:
            print("** no instance found **")
        else:
            print(objdict["{}.{}".format(arg_list[0], arg_list[1])])

    def do_destroy(self, arg):
        """ Delete a class instance of a given id."""
        arg_list = parse(arg)
        objdict = storage.all()
        if len(arg_list) == 0:
            print("** class name missing **")
        elif arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        elif len(arg_list) == 1:
            print("** instance id missing **")
        elif "{}.{}".format(arg_list[0],
                            arg_list[1]) not in objdict.keys():
            print("** no instance found **")
        else:
            del objdict["{}.{}".format(arg_list[0], arg_list[1])]
            storage.save()

    def do_all(self, arg):
        """ Display string representations of all instances of a given class.
        If no class is specified, displays all instantiated objects."""
        arg_list = parse(arg)
        if len(arg_list) > 0 and arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
        else:
            object_list = []
            for obj in storage.all().values():
                if len(arg_list) > 0 and arg_list[0] == obj.__class__.__name__:
                    object_list.append(obj.__str__())
                elif len(arg_list) == 0:
                    object_list.append(obj.__str__())
            print(object_list)

    def do_count(self, arg):
        """ Retrieve the number of instances of a given class."""
        arg_list = parse(arg)
        count = 0
        for obj in storage.all().values():
            if arg_list[0] == obj.__class__.__name__:
                count += 1
        print(count)

    def do_update(self, arg):
        """ Update a class instance of a given id by adding or updating
        a given attribute key/value pair or dictionary."""
        arg_list = parse(arg)
        object_dict = storage.all()

        if len(arg_list) == 0:
            print("** class name missing **")
            return False
        if arg_list[0] not in HBNBCommand.__classes:
            print("** class doesn't exist **")
            return False
        if len(arg_list) == 1:
            print("** instance id missing **")
            return False
        if "{}.{}".format(arg_list[0], arg_list[1]) not in object_dict.keys():
            print("** no instance found **")
            return False
        if len(arg_list) == 2:
            print("** attribute name missing **")
            return False
        if len(arg_list) == 3:
            try:
                type(eval(arg_list[2])) != dict
            except NameError:
                print("** value missing **")
                return False

        if len(arg_list) == 4:
            obj = object_dict["{}.{}".format(arg_list[0], arg_list[1])]
            if arg_list[2] in obj.__class__.__dict__.keys():
                value_type = type(obj.__class__.__dict__[arg_list[2]])
                obj.__dict__[arg_list[2]] = value_type(arg_list[3])
            else:
                obj.__dict__[arg_list[2]] = arg_list[3]
        elif type(eval(arg_list[2])) == dict:
            obj = object_dict["{}.{}".format(arg_list[0], arg_list[1])]
            for key, value in eval(arg_list[2]).items():
                if (key in obj.__class__.__dict__.keys() and
                        type(obj.__class__.__dict__[key]) in
                        {str, int, float}):
                    value_type = type(obj.__class__.__dict__[key])
                    obj.__dict__[key] = value_type(value)
                else:
                    obj.__dict__[key] = value
        storage.save()


if __name__ == "__main__":
    HBNBCommand().cmdloop()
