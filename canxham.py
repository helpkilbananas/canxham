from datetime import datetime as dt
from secrets import choice as rand
from sys import argv
import requests as r
import zipfile
import os

class Exam:
    def __init__(self):
        if len(argv) != 2 and argv[1] not in ["adv", "basic"]:
            print("\nUsage:  canxham.py  'basic' { or } 'adv'  \n")
            exit(1)

        if argv[1] == "adv":
            self.question_total = 50
        else:
            self.question_total = 100
        
        self.pwd = os.path.dirname(__file__)
        self.file_name = f"amat_{argv[1]}_quest"
        self.url = f"http://apc-cap.ic.gc.ca/datafiles/{self.file_name}.zip"

        self.score = 0

    def update(self):
        print(f"Fetch latest {argv[1]} exam data {self.url}...")
        download = r.get(self.url)
        print("Done\n")
        
        with open(f"{self.pwd}{self.file_name}.zip", "wb") as f:
            f.write(download.content)
        zip_file = zipfile.ZipFile(f"{self.pwd}{self.file_name}.zip")
        zip_file.extract(f"{self.file_name}_delim.txt")
        os.remove(f"{self.pwd}{self.file_name}.zip")

        with open(f"{self.pwd}{self.file_name}_delim.txt", "rb") as f:
            data = f.readlines()
        d = [i.decode("latin").split(";") + ["\r"] for i in data]
        self.data = [f'{";".join(i)}' for i in sorted(d)]
        os.remove(f"{self.pwd}{self.file_name}_delim.txt")

    def start(self):
        self.date = dt.utcnow().strftime("%Y-%m-%d-%H%M")

        data = []
        for line in self.data:
            sections = line.split("\r")
            for i in range(len(sections)):
                data.append(sections[i].replace("\r", ""))
        self.data = data

        question_list = []
        for i in range(self.question_total):
            question = rand(self.data)
            while f"{argv[1][0].upper()}-00" not in question:
                question = rand(self.data)
            
            self.data.pop(self.data.index(question))
            
            question = ";".join(question.split(";")[:6])
            question_list.append(question.split(";"))
            
            question = "\n".join(question_list[i][:2]).upper()
            answers = question_list[i][2:]
            correct = answers[0]
            
            answer_list = []
            for j in range(4):
                answer_list.append(rand(answers))
                answers.pop(answers.index(answer_list[j]))
            
            print(f"{question}\n")
            
            abc = ["a", "b", "c", "d"]
            for j in range(len(answer_list)):
                print(f" {abc[j]}):  {answer_list[j]}\n")
            
            try:
                answered = str(input("\nYour Answer: ").lower())
                while answered not in abc:
                    print(f"Invalid choice:  [{answered}]")    
                    answered = str(input("\nYour Answer: ").lower())
            except KeyboardInterrupt:
                if self.score:
                    score = self.score / self.question_total * 100
                else:
                    score = 0
                print(f"\nScore:  {score}%\n")
                exit(2)

            if answer_list[abc.index(answered)] == correct:
                print(f"Correct!  The answer is:\n{correct} ({answered})\n")
                self.score += 1
            else:
                print(f"Incorrect!  The answer is:\n{correct} ({abc[answer_list.index(correct)]})\n")
            
            exam_log = [f"\n#{i + 1} {question}\n", 
                       [f"{abc[j]}):  {answer_list[j]}\n" for j in range(len(answer_list))],
                       f"\nAnswered:  {answer_list[abc.index(answered)]} ({answered})\n",
                       f"\nCorrect:  {correct} ({abc[answer_list.index(correct)]})\n",
                       f"\nCurrent score: {self.score}",
                       f"\nCurrent mark: {self.score / self.question_total * 100}%\n"]

            with open(f"{self.pwd}{argv[1]}_EXAM-{self.date}.txt", "a") as f:
                for j in range(len(exam_log)):
                    f.write("".join(exam_log[j]))
                    

exam = Exam()
exam.update()
exam.start()

if exam.score:
    score = exam.score / exam.question_total * 100
else:
    score = 0

print(f"\nScore:  {score}%\n")


