#!pip install llama-index
#!pip install openai
#!pip install langchain
#!pip install tiktoken (MAC-re kellett terminalban panaszkodott miatta)
#!pip install colorama


import argparse
import os
import sys
import subprocess
import pkg_resources


# Provide the path to the folder containing the PDF documents
folder_path = "./"


#Store what OS we are running on. This will be important when composing links to PDF pages.
os_name = sys.platform

# Conditional branch based on the operating system
if os_name.startswith('linux'):
    # Linux-specific code
    print("Running on Linux")
    # Add your Linux-specific code here

elif os_name.startswith('darwin'):
    # macOS-specific code
    print("Running on macOS")
    # Add your macOS-specific code here

elif os_name.startswith('win'):
    # Windows-specific code
    print("Running on Windows")
    # Add your Windows-specific code here

else:
    # Code for other operating systems
    print("Running on an unrecognized operating system")
    # Add code for other operating systems here

    # Create an ArgumentParser object
parser = argparse.ArgumentParser(prog='app.py',
    description="""This application takes a LaTeX file and performs grammar checking and stlye optimization on it.
\n
    ---:» You have to specify an OpenAI API key for this tool to work. «:---\n
\n
    By default, the application will assume that the first command line argument is going to be your filename,
    and assume that it will find the documents at the $DOCUMENTSPATH location you specified in the
    configuration.

    For example:
    > python app.py mylatexfile.tex"

    You can also use the -docpath argument to tell the application to look for the documentation in a different folder.

For example:
    > python app.py mylatexfile.tex -docpath "../omnetpp-6.0.1/doc/"

    """,
    epilog=''
)

# Add an optional argument for the path
parser.add_argument('-filename', help = "The filename of the LaTEX file you wish to optimize.", required=True)

# Add an optional argument for the path
parser.add_argument('-docpath', default='./', help = "The path of the directory containing your documents to search", required=False)

# Parse the command-line arguments
args = parser.parse_args()

# Access the question argument
filename = args.filename

# Access the optional path argument
docpath = args.docpath

#Check if there is an OpenAI key available. (There should be an openai_key.txt file in the same directory as searchPDF.py)
if os.path.exists("openai_key.txt"):
    print("OpenAI key found, proceeding.")
else:
    print(Fore.RED+"This program cannot function without an OpenAI key. There must be an"+Fore.CYAN+" openai_key.txt"+Fore.RED+
    " file in the same directory as searchPDF, and it must contain your own unique OpenAI API key. Refer to the internet on how to get one."
    +Fore.WHITE)
    sys.exit()

    #List of required packages
packages = [
    "llama-index",
    "openai",
    "langchain",
    "tiktoken",
    "colorama",
    "texttable",
    "uuid",
]
#Check for required packages and install them if needed.
def check_package(package_name):
    try:
        dist = pkg_resources.get_distribution(package_name)
        #print(f"{package_name} {dist.version} is already installed.")
        return True
    except pkg_resources.DistributionNotFound:
        print(f"{package_name} is not installed.")
        return False

def install_package(package_name):
    subprocess.check_call(["pip", "install", package_name])
    print(f"{package_name} has been installed.")

#Install missing packages
for package in packages:
    if not check_package(package):
        install_package(package)

def printhelp():
    print ("""This application takes a LaTeX file and performs grammar checking and stlye optimization on it.
\n
    ---:» You have to specify an OpenAI API key for this tool to work. «:---\n
\n
    By default, the application will assume that the first command line argument is going to be your filename,
    and assume that it will find the documents at the $DOCUMENTSPATH location you specified in the
    configuration.

    For example:
    > python app.py mylatexfile.tex" - This is a required argument.

    You can also use the -docpath argument to tell the application to look for the documentation in a different folder.

For example:
    > python app.py mylatexfile.tex -docpath "../omnetpp-6.0.1/doc/"

    """)

#Check command line arguments, we need a filename at least.
if len(sys.argv) < 1:

       printhelp()

from colorama import Fore
import uuid
from langchain.llms import OpenAI
import openai

#get OPENAI_API_KEY from config file
def load_openai_key():
    
    with open('openai_key.txt', 'r') as file:
        key = file.read().strip()
    return key

# Set key from config file
openai_key = load_openai_key()
os.environ['OPENAI_API_KEY'] = openai_key


"""llm = OpenAI(temperature=0)
llm.model_name="gpt-4-32k" #you can also try "text-davinci-003", or "gpt-3.5-turbo-16k"
llm.top_p = 0.2
llm.openai_api_key = openai_key"""

#Assemble file path and name
if len(args.docpath)>1 and len(args.filename)>0:
    filetoload = args.docpath + args.filename
else: 
    print(Fore.RED+"There is a problem with the input parameteres!"+Fore.RESET)
    printhelp()
    exit(1)

instructions = "You are a expert latex editor. Analize the following LaTeX for any grammatical errors and correct them. Retain the formating of the LaTeX file, and improve it to be more concise, to the point and easy to read and understand. Please display the new file and a summary of changes at the bottom. This is what needs to be anaized:/n"

with open(filetoload, 'r') as file:
    file_contents = file.read()

input_tex = instructions + file_contents

def unique_file(base_filename, extension):
    while True:
        unique_name = f"{base_filename}_{uuid.uuid4().hex[:6]}.{extension}"
        if not os.path.exists(unique_name):
            return unique_name


prompt = [""]
prompt[0] = input_tex

"""message_log = [
    {"role": "system", "content": "You are a expert latex editor. You only return valid latex. Everything you return is directly inserted into a latex document and intepreted as latex code."}
]"""

message_log = [
    {"role": "system", "content": "You are a expert latex editor. You only return valid latex. Everything you return is directly inserted into a latex document and intepreted as latex code."}
]
message_log.append({"role": "user", "content": input_tex})
def send_message(message_log):
    openai.api_key = openai_key
    print(Fore.BLUE+"Processing file, please be patient."+Fore.RESET)
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k", #"gpt-4-32k" #you can also try "text-davinci-003", or "gpt-3.5-turbo-16k"
        messages=message_log,
        #max_tokens=3000,
        stop=None,
        temperature=0.7,
        stream=True,
    )

response = send_message(message_log)

content_list = []

for item in response:
    if 'delta' in item['choices'][0] and 'content' in item['choices'][0]['delta']:
        content = item['choices'][0]['delta']['content']
        content_list.append(content)

final_content = ''.join(content_list)

newfilename = unique_file(args.filename, "edited")

with open(newfilename, 'w') as f:
    f.write(final_content)
print("Output file has been written as: "+newfilename)
