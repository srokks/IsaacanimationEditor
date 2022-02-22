import os
# All files and directories ending with .txt and that don't begin with a dot:
def convert():
    try:
        counter = 0
        for root, dirs, files in os.walk("./ui_files/", topdown=False):
            for file in files:
                if file[-2::] == 'ui':
                    temp_name = file[:-3:]
                    command = f"pyuic5 ./ui_files/{temp_name}.ui -o " \
                              f"./designer_widgets/{temp_name}.py"
                    os.system(command)
                    counter += 1
        print(f'Converted {counter} *.ui files!')
    except:
        print('Error')

if __name__ == '__main__':
    convert()