Documentation of Project Implementation for IPP 2022/2023 <br>
Name and surname: Sviatoslav Shishnev <br>
Login: xshish02 <br>

Overview
This implementation of an interpreter for a programming language was developed using an object-oriented design approach. The implementation resulted in several classes, including the Analisator and Frame classes, which handle semantic analysis and frame-related operations, mostly operations with variables. The GlobalFrame class inherits from the Frame class and handles operations related to global frames, such as setting and getting labels.

Initially, it was seen as a good solution to separate semantic and syntax analysis to simplify the code and ensure modularity. However, during the implementation process, it became apparent that it was more efficient to combine semantic and syntax analysis. This allowed the avoidance of implementing the same solution, such as instruction opcode parsing, twice.

In addition to the object-oriented design approach that was employed in this implementation, it should be noted that the design of the Analisator class encountered some challenges. The class has many methods, and its size could have been reduced by creating smaller, more focused classes that handle specific tasks. This could have made the code more modular, easier to read, and easier to maintain. Nevertheless, the Analisator class, as it is, is still functional and meets most of the requirements of the project.

Ideas of Implementations
Object-oriented design approach
Separation of semantic and syntax analysis
XML validation of source code
Details of Implementations
Analisator class: Handles the interpretation of the program. It contains many methods that could be reduced by creating smaller, more focused classes that handle specific tasks.
Frame class: Handles frame-related operations, mostly operations with variables.
GlobalFrame class: Inherits from the Frame class and handles operations related to global frames, such as setting and getting labels.
XML_validator class: Parses and validates the XML source code.