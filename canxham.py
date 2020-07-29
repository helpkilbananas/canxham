from datetime import datetime as dt
from secrets import choice as rand
from sys import argv
import requests as r
import zipfile
import os

class Exam:
    def __init__(self):
        self.pwd = os.path.dirname(__file__)
        self.score = 0
        self.questions = []
        if len(argv) == 2 and argv[1] in ["adv", "basic"]:
            self.names = f"amat_{argv[1]}_quest"
            self.url = f"http://apc-cap.ic.gc.ca/datafiles/{self.names}.zip"
        else:
            print("\nUsage:  canxham.py  'basic' { or } 'adv'  \n")
            exit(1)

        if argv[1] == "adv":
            self.question_total = 50
        else:
            self.question_total = 100

    def update(self):
        print(f"Fetch latest {argv[1]} exam data {self.url}...")
        download = r.get(self.url)
        print("Done\n")
        
        with open(f"{self.pwd}{self.names}.zip", "wb") as f:
            f.write(download.content)
        zip_file = zipfile.ZipFile(f"{self.pwd}{self.names}.zip")
        zip_file.extract(f"{self.names}_delim.txt")

        with open(f"{self.pwd}{self.names}_delim.txt", "rb") as f:
            data = f.readlines()
        d = [i.decode("latin").strip("\r\n").split(";") + ["\r"] for i in data]
        self.data = sorted(d)

        with open(f"{self.pwd}{self.names}.txt", "w") as f:
            for i in self.data:
                f.write(f'{";".join(i)}\r\n')

    def start(self):
        self.date = dt.utcnow().strftime("%Y-%m-%d-%H%M")
        with open(f"{self.pwd}{self.names}.txt", "r") as f:
            self.data = f.readlines()

        data = []
        for line in self.data:
            sections = line.split("\r")
            for i in range(len(sections)):
                data.append(sections[i].replace("\r", ""))
        self.data = data

        self.quests = []
        for i in range(self.question_total):
            quest = rand(self.data)
            while f"{argv[1][0].upper()}-00" not in quest:
                quest = rand(self.data)
            
            self.data.pop(self.data.index(quest))
            
            quest = ";".join(quest.split(";")[:6])
            self.quests.append(quest.split(";"))
            
            question = "\n".join(self.quests[i][:2]).upper()
            answers = self.quests[i][2:]
            correct = answers[0]
            
            ans = []
            for j in range(4):
                ans.append(rand(answers))
                answers.pop(answers.index(ans[j]))
            
            print(f"{question}\n")
            
            abc = ["a", "b", "c", "d"]
            for j in range(len(ans)):
                print(f"{abc[j]}):  {ans[j]}")
            
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

            if ans[abc.index(answered)] == correct:
                print(f"Correct!  The answer is:\n{correct} ({answered})\n")
                self.score += 1
            else:
                print(f"Incorrect!  The answer is:\n{correct} ({abc[ans.index(correct)]})\n")
            
            questions = [f"\n#{i + 1} {question}\n", 
                        [f"{abc[j]}):  {ans[j]}\n" for j in range(len(ans))],
                        f"\nAnswered:  {ans[abc.index(answered)]} ({answered})\n",
                        f"\nCorrect:  {correct} ({abc[ans.index(correct)]})\n",
                        f"\nCurrent score: {self.score}",
                        f"\nCurrent mark: {self.score / self.question_total * 100}%\n"]

            self.questions.append(questions)

            with open(f"{self.pwd}{argv[1]}_exam-{self.date}.txt", "a") as f:
                for j in range(len(questions)):
                    f.write("".join(questions[j]))
                    

exam = Exam()
exam.update()
exam.start()

if exam.score:
    score = exam.score / exam.question_total * 100
else:
    score = 0

print(f"\nScore:  {score}%\n")


