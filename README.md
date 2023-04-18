Documentation of Project Implementation for IPP 2022/2023 <br>
Name and surname: Sviatoslav Shishnev <br>
Login: xshish02 <br>

## Overview <br>
<p>This implementation of an interpreter for a programming language was developed using an object-oriented design approach. The implementation resulted in several classes, including the Analisator and Frame classes, which handle semantic analysis and frame-related operations, mostly operations with variables. The GlobalFrame class inherits from the Frame class and handles operations related to global frames, such as setting and getting labels.</p>

<p>Initially, it was seen as a good solution to separate semantic and syntax analysis to simplify the code and ensure modularity. However, during the implementation process, it became apparent that it was more efficient to combine semantic and syntax analysis. This allowed the avoidance of implementing the same solution, such as instruction opcode parsing, twice.</p>

<p>In addition to the object-oriented design approach that was employed in this implementation, it should be noted that the design of the Analisator class encountered some challenges. The class has many methods, and its size could have been reduced by creating smaller, more focused classes that handle specific tasks. This could have made the code more modular, easier to read, and easier to maintain. Nevertheless, the Analisator class, as it is, is still functional and meets most of the requirements of the project.</p>

## Ideas of Implementations <br>
- The concept of frames is used to represent local temporary and global frames. Local frames are stored in a stack, and the last local frame is always accessible. Variables are stored in Python dictionaries, which are used as hash tables.
- XML parsing and processing is carried out using a tree element library. Which represents document as 'root' oobject, that contains all elements and subelements
- The Analisator class uses a dictionary to represent valid opcode instructions. The keys of the dictionary are the opcodes, and the values represent the corresponding instruction data. The instruction data values are divided into groups based on their operands. This optimization ensures that the code is more readable and structured, which in turn makes it easier to maintain and modify.
## Details of Implementations <br>
<p>Analisator class: This class was not implemented efficiently and did not follow OOP principles. It contained too many methods and was difficult to read and understand. However, it served as a learning experience in the importance of considering design before implementation.<br>

The class operates on attributes such as the global frame, local frames stack, and temporary frame, all of which are instances of the Frame class. Analisator class has methods to define, check the existence of, get, and set variables by sending messages to the Frame class.<br>

The class also contains a dictionary of valid opcodes, and the parse_instr method selects the commands to execute based on the opcode. In an ideal implementation, parse_instr should decide which method of Analisator to invoke. The selected commands interpret one instruction's semantics.<br>

These commands use the class's methods to set or get variables and to determine the set of commands to execute, which can be arithmetic instructions (arithmetic_inst) or relation instructions (relation_instr). The parse_instr method is called by the analise method on each element of the XML code provided by the source file. The analise method simply loops through all XML elements sorted by attributes.</p>

Frame class: This class contains dictionaries that represent tables of variables related to each frame. The GlobalFrame class inherits this class and adds a dictionary of labels. The class has methods to define, check the existence of, get, and set variables and labels.<br>

Analisator class:

- This class is responsible for analyzing the source code of a program and interpret it.
- It operates on attributes such as the global frame, local frames stack, and temporary frame, all of which are instances of the Frame class.
- The Analisator class contains a dictionary of valid opcodes, and the parse_instr method selects the commands to execute based on the opcode.
- Analisator class has methods to define, check the existence of, get, and set variables by sending messages to the Frame class.
- The class also contains a set of commands that interpret the semantics of each opcode.
- The Analisator class interacts with the Frame class to access and modify variables in the different frames.<br>

Frame class:

- This class is responsible for representing the frames of a program.
- It contains dictionaries that represent tables of variables related to each frame.
- The Frame class has methods to define, check the existence of, get, and set variables and labels.
- The GlobalFrame class inherits from the Frame class and adds a dictionary of labels to handle global frames.
- The Frame class interacts with the Analisator class to provide access to variables and labels.

Variable class:
- Represents variable with value and type attributes 

## Summary 
Through the process of implementing this project, I gained valuable experience and learned the importance of considering design before implementation. Specifically, I learned that taking an object-oriented design approach is essential for creating maintainable, readable, and modular code. Unfortunately, the implementation of this project did not follow object-oriented principles and is therefore not a good example of good design. However, this experience has provided me with a deeper understanding of the importance of good design and will undoubtedly inform my future work.<br>Overall, this project has reinforced the importance of prioritizing design considerations in software development projects, and the benefits that come with taking a methodical, structured approach to coding.