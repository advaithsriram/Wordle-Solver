# Wordle-Solver
A simple python program that can solve the daily NY Times' Wordle

# How to use the program
1) Download the files wordle_solver.py and wordle_words.txt
2) Run the wordle_solver.py file
3) Have https://www.nytimes.com/games/wordle/index.html on your browser and type in the word that the program suggests
4) Based on the response (see images below), type in the number corresponding to it  
Green - 2  
Yellow - 1  
Grey - 0 


![Example1 (Opera) Yellow-Grey-Grey-Grey-Grey](https://github.com/advaithsriram/Wordle-Solver/blob/main/images/example1.png)  

In the above image, the corresponding text input into the program would be 10000  

![Example2 (Those) Yellow-Yellow-Green-Grey-Grey](https://github.com/advaithsriram/Wordle-Solver/blob/main/images/example2.png)  

Similarly, in the above image, the corresponding text input into the program would be 11200  

5) With each turn, the confidence value of the suggested answer will increase. Repeat steps 3 and 4 until the program returns a word with a 100% confidence value. This is the answer to the Wordle Puzzle.

# Video Demonstration
Please watch the video for further clarifications
![Video Demonstration](https://github.com/advaithsriram/Wordle-Solver/blob/main/wordle%20mar6.mov)
