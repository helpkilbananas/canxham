from datetime import datetime as dt
from secrets import choice as rand
from zipfile import ZipFile
from sys import argv, exit
import requests as r
import os

class Exam:
    def __init__(self):
        self.french = 0
        if "-mfr" in argv:
            argv.pop(argv.index("-mfr"))
            self.french = 1
        
        if len(argv) == 2 and "adv" in argv:
            self.exam_type = "adv"
        elif len(argv) == 2 and "basic" in argv:
            self.exam_type = "basic"
        else:
            print("\nUsage:  python canxham.py  'basic' { or } 'adv'")
            print("Mode Français:  Ajouter  '-mfr'  au fin\n")
            exit(1)

        if self.exam_type == "adv":
            self.question_total = 50
        else:
            self.question_total = 100
        
        self.pwd = os.path.dirname(__file__)
        self.file_name = f"amat_{self.exam_type}_quest"
        self.file_path = os.path.join(self.pwd, self.file_name)
        self.log_path = os.path.join(self.pwd, self.file_name[:-6] + "_EXAM")
        self.url = f"https://apc-cap.ic.gc.ca/datafiles/{self.file_name}.zip"

        self.score = 0

    def update(self):
        if self.french:
            print(f"Téléchargement des fichiers d'exam {self.exam_type} {self.url}...")
        else:
            print(f"Fetch latest {self.exam_type} exam data {self.url}...")
        
        try:        
            download = r.get(self.url)
        except:
            print("Network Error/Erreur de connexion")
            print("Assurez-vous avoir une connexion Internet, et réessayez.")
            print("Make sure you have an Internet connection, and try again.")
            exit(3)

        if not download.ok:
            print(f"\n{download.url}: {download.status_code} {download.reason}")
            print("Try again later/Réessayez plus tard\n")
            exit(download.status_code)

        print("Done!\n\nGood Luck et Bonne Chance DE VO1ZXZ\n\n")
        
        with open(f"{self.file_path}.zip", "wb") as f:
            f.write(download.content)
        
        with ZipFile(f"{self.file_path}.zip") as f: 
            f.extract(f"{self.file_path}_delim.txt")
        os.remove(f"{self.file_path}.zip")

        with open(f"{self.file_path}_delim.txt", "rb") as f:
            data = f.readlines()
        os.remove(f"{self.file_path}_delim.txt")
        
        d = [i.decode("latin").split(";") + ["\r"] for i in data]
        self.data = [f'{";".join(i)}' for i in sorted(d)]

        data = []
        for line in self.data:
            sections = line.split("\r")
            for i in range(len(sections)):
                data.append(sections[i].replace("\r", ""))
        self.data = data[:-2:2]

    def start(self):
        self.date = dt.utcnow().strftime("%Y-%m-%d-%H%M")

        question_list = []
        for i in range(self.question_total):
            question = rand(self.data)
            question_id = question.split(';')[0]
            category = question_id[:-3]

            self.data = [j for j in self.data if category not in j.split(";")[0][:-3]]

            if self.french:
                question = ";".join(question.replace("\n", "").split(";")[6:])
            else:
                question = ";".join(question.split(";")[1:6])
            question_list.append(question.split(";"))
            
            question = "\n".join([question_id] + question_list[i][:1]).upper()

            if self.french:
                answers = question_list[i][1:-1]
            else:
                answers = question_list[i][1:]
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
                if self.french:
                    answered = str(input("\nVotre Réponse: ").lower())
                else:
                    answered = str(input("\nYour Answer: ").lower())
                
                bye = ["exit", "quit", "done", "bye", "fin", ":q", "73"]
                while answered not in abc:
                    if answered in bye:
                        raise KeyboardInterrupt

                    if self.french:
                        print(f"Choix mal compris:  [{answered}]")
                    else:
                        print(f"Invalid choice:  [{answered}]")    
                
                    if self.french:
                        answered = str(input("\nVotre Réponse: ").lower())
                    else:
                        answered = str(input("\nYour Answer: ").lower())

            except KeyboardInterrupt:
                if self.score:
                    score = self.score / self.question_total * 100
                else:
                    score = 0
                print(f"\nScore:  {score}%\n")
                exit(2)

            if answer_list[abc.index(answered)] == correct:
                if self.french:
                    print("Correcte!  Bonne réponse:")
                    print(f"{correct} ({answered})\n\n")
                else:
                    print("Correct!  The answer is:")
                    print(f"{correct} ({answered})\n\n")
                self.score += 1
            else:
                if self.french:
                    print("Incorrecte!  Bonne réponse:")
                    print(f"{correct} ({abc[answer_list.index(correct)]})\n\n")
                else:
                    print(f"Incorrect!  The answer is:")
                    print(f"{correct} ({abc[answer_list.index(correct)]})\n\n")
            
            exam_log = [f"\n#{i + 1} {question}\n", 
                       [f"{abc[j]}):  {answer_list[j]}\n" for j in range(len(answer_list))],
                       f"\nAnswered:  {answer_list[abc.index(answered)]} ({answered})\n",
                       f"\nCorrect:  {correct} ({abc[answer_list.index(correct)]})\n",
                       f"\nCurrent score: {self.score}",
                       f"\nCurrent mark: {self.score / self.question_total * 100}%\n"]

            with open(f"{self.log_path}-{self.date}.txt", "a") as f:
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

