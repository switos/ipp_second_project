Documentation of Project Implementation for IPP 2022/2023
Name and surname: Sviatoslav Shishnev
Login: xshish02

This implementation of an interpreter for a programming language was developed using an object-oriented design approach. The implementation resulted in several classes, including the Analisator and Frame classes, which handle semantic analyse and frame-related operations, mostly operatins with variables. The GlobalFrame class inherits from the Frame class and handles operations related to global frames, such as setting and getting labels.

Additionally, the XML_validator class is responsible for parsing and validating the XML source code, while the Analisator class handles the actual interpretation of the program. Initially, it was seen as a good solution to separate semantic and syntax analysis to simplify the code and ensure modularity. However, during the implementation process, it became apparent that it was more efficient to combine semantic and syntax analysis. This allowed the avoidance of implementing the same solution, such as instruction opcode parsing, twice. 

In addition to the object-oriented design approach that was employed in this implementation, it should be noted that the design of the Analisator class encountered some challenges. The class has many methods, and its size could have been reduced by creating smaller, more focused classes that handle specific tasks. This could have made the code more modular, easier to read, and easier to maintain. Nevertheless, the Analisator class, as it is, is still functional and meets most of the requirements of the project.


