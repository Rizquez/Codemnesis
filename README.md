# Codemnesis - v.0.14.0 (*Development temporarily halted*)

## 🧾 Project description

**Codemnesis** is a tool that automatically analyzes code repositories to generate clear and useful documentation.

Its goal is to save developers time by automatically creating files such as README, flowcharts, and explanations of each module, without relying on manual writing.

Through static code analysis, it provides a comprehensive overview of the project, its dependencies, and its internal structure.

## 📑 Context

Technical documentation often lags behind the pace of development, creating three common problems: **steep learning curves**, **scattered knowledge** and **costly maintenance**. Manually updating READMEs, diagrams, and docstrings does not scale and ends up out of sync with the code.

**Codemnesis** was created to automate this *invisible work*: it analyzes a repository and generates **explanatory documentation** directly from the code, describing flows, dependencies, responsibilities, and possible improvements.

### Who is it useful for?

- **Teams** that need quick onboarding and living documentation.  
- **Freelancers or consultants** who deliver projects with professional README files.  
- **Maintainers or reviewers** looking to detect couplings or fragile points.  
- **Technical portfolios** that want to reflect architecture and design decisions.

### Examples of use

- Inherit a project without documentation and obtain an **initial technical overview**.
- Prepare a **release** and validate documentation and dependencies.
- Perform automated **technical reviews** to identify *magic* functions or poorly cohesive modules.

## 🛠️ Key features

- Browse the repository filtering by a specific programming language.
- Detection of documentation on classes, methods, decorators, and functions.
- Obtaining minimum metrics for each module based on the elements contained in the module.

### Generated documents

- **Readme** file generated based on existing documentation in the repository code.
- **Graph** associated with the map of import dependencies between modules.
- **Report** with relevant information on common indicators and interpreted metrics.

> [!IMPORTANT]
> Supported programming languages: Python and C#.

## 💽 Installation (Windows)

Clone this repository (ssh):
```sh
git clone git@github.com:Rizquez/Codemnesis.git
```

Access the project directory:
```sh
cd Codemnesis
```

Create a development environment using the **virtualenv** library:
```sh
virtualenv venv
```

If you do not have the library installed, you can run:
```sh
python -m venv env
```

Activate the development environment:
```sh
venv\Scripts\activate
```

Once the environment is activated, install the dependencies:
```sh
pip install -r requirements.txt
```

## 🚀 Execution

### Console

To run the application from the console, you can use the following command shown as an example:

```sh
python main.py --framework=... --repository=... --output=... --excluded=...
```

Where:

- **framework:** Programming languages and frameworks supported by the algorithm.
- **repository:** Directory of the repository that hosts the project.
- **output (optional):** Directory where the generated files will be saved. If not specified, the folder where the files are stored will be created in the *root of this project*.
- **excluded (optional):** Additional files and extensions to exclude from the scan, separated by commas if multiple are specified.

> [!NOTE]
> For more details about the parameters and execution arguments, see the file located at: *handlers/arguments.py*

## 📂 Project structure

The main files are organized into:

```
Codemnesis/
├── common
│   ├── constants.py
│   └── settings.py
├── handlers
│   ├── arguments.py
│   └── logger.py
├── helpers
│   └── traces.py
├── src
│   ├── analyzers
│   │   ├── __init__.py
│   │   ├── csharp.py
│   │   └── python.py
│   ├── generators
│   │   ├── __init__.py
│   │   ├── graphic.py
│   │   ├── readme.py
│   │   └── report.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   └── metrics.py
│   ├── tools
│   │   ├── docstring.py
│   │   ├── fixers.py
│   │   ├── nums.py
│   │   └── scanner.py
│   ├── utils
│   │   ├── maps.py
│   │   └── metrics.py
│   └── execute.py
├── templates
│   └── report.docx
├── .gitignore
├── LICENSE
├── main.py
├── README.md
└── requirements.txt
```

## 🎯 Additional considerations for developers

### Forward References (PEP 484)

The project uses *Forward References* according to *PEP 484*. By using `TYPE_CHECKING`, the import of a class is only performed at static type checking time (for example, with *mypy*). During execution, `TYPE_CHECKING` evaluates to `False`, preventing the actual import. This optimizes performance and allows forward references to classes.

Example:

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models import MyFirstClass

class MySecondClass:
    def do_something(self, first: 'MyFirstClass') -> None:
        pass
```

### Convention for private attributes and methods (Name mangling)

In Python, there is no true encapsulation as in other languages (Java, C++), but it can be simulated using conventions. In this project, the mechanism known as `Name Mangling` is used to name private attributes and methods, which involves using a double underscore (__) at the beginning of the name.

This mechanism not only indicates the intention to keep these elements private, but Python also internally modifies their names to avoid collisions, especially in inherited classes.

How does it work? When an attribute is defined as `__my_attribute` within a class, Python internally converts it to `_ClassName__my_attribute`, making accidental or unwanted external access difficult.

Example:

```python
class Engine:
    def __init__(self):
        self.__status = "on"

    @property
    def status(self):
        return self.__status

m = Engine()
print(m.status)            # ✔️ Output: on
print(m.__status)          # ❌ Error: AttributeError
print(m._Engine__status)    # ✔️ Access possible, but not recommended (Output: on)
```
> [!WARNING]
> Although technically accessible via the mangled name, its direct use is discouraged outside the context of the class itself.

## 📖 Additional documentation

- [Graphviz](https://graphviz.org/)
- [Jinja2](https://jinja.palletsprojects.com/en/stable/)

## 🔒 License

This project is licensed under the *MIT* license, which allows its use, distribution, and modification under the conditions specified in the *LICENSE* file.

## ⚙ Contact, support, and development

- Pedro Rizquez: pedro.rizquez.94@hotmail.com