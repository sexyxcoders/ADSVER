import os


class FileManage:
    def __init__(self):
        self.file = ""

    def saveFileInfo(self, fileName):
        self.file = fileName

    def readFile(self, file):
        with open(file, 'r') as f:
            self.text = f.read()
            return self.text
        
    def writeFile(self, file, content):
        with open(file, 'w', encoding = "utf-8") as f:
            f.write(content)
            return True
        
    def writePretty(self, file, content: list):
        with open(file, 'w', encoding = "utf-8") as f:
            for line in content:
                f.write(line + "\n")
            return True
        
    def deleteFile(self, file):
        try:
            os.remove(file)
            return True
        except Exception as e:
            print(e)
            return False
    
    def makeMediaFolder(self, folderName):
        try:
            os.mkdir(folderName)
            return True
        except Exception as e:
            print(e)
            return False
        
    def deleteMediaFolder(self, folderName):
        try:
            for file in os.listdir(folderName):
                os.remove(f"{folderName}/{file}")
            os.rmdir(folderName)
            return True
        except Exception as e:
            print(e)
            return False
        
    
class FileDebug:
    def __init__(self) -> None:
        pass

    def debugFile(self, content, file = "debug.txt"):
        with open(file, 'a', encoding = "utf-8") as f:
            f.write(content + "\n")
            return True

