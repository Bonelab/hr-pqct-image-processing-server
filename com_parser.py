


class Parser:
    def __init__(self):
        self.com_file = None
        self.data = {}

    def parse_com(self, file_path):
        command_file = {}
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in lines:
                line = line.strip("$").strip()
                if "!" in line:
                    sp = line.split("!")
                    line = sp[0]
                if ":==" in line:
                    split = line.split(":==")
                    if split[1] != "":
                        command_file[split[0].strip()] = split[1].strip()
        return command_file
