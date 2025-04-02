# saveMyRepeater
saveMyRepeater is a Burp Suite Community extension that allows users to save and restore selected Repeater requests.

![image](https://github.com/user-attachments/assets/b8273c64-8347-40c9-aefe-64427c27dfb0)

# Installation

1.	Download Burp Suite : http://portswigger.net/burp/download.html
2.	Download Jython standalone JAR: http://www.jython.org/downloads.html
3.	Open burp -> Extender -> Options -> Python Environment -> Select File -> Choose the Jython standalone JAR
5.	Download the extension saveMyRepeater.py file.
6.	Open Burp -> Extender -> Extensions -> Add -> Choose the file.


## Usage

### Save a repeater tab
- Go to to the saveMyRepeater tab
- Select the directory where you want to save the tab file; the default is ```.```
- Go to the repeater tab you want to save.
- Press right-click -> Extensions -> saveMyRepeater -> Save this repeater tab

![image](https://github.com/user-attachments/assets/61c059ae-5434-432f-9ec8-0bb46b8d8e66)

- Define the name of the tab to save

![image](https://github.com/user-attachments/assets/b56775bd-741d-4018-a25c-0f76bd27c8ee)

### Load a repeater tab
- Go to to the saveMyRepeater tab
- Select the directory where you want to load the tab file; the default is ```.```
- Select the repeater file you want to load
- Click "Load the repeater tab"

### Copy the response of a saved repeater tab
The plugin cannot load the response content into the repeater, so it can only be provided by pasting it into the clipboard.

- Go to to the saveMyRepeater tab
- Select the directory where you want to load the tab file; the default is ```.```
- Select the repeater file you want to copy the saved response
- Click "Copy to the clipboard the response"


## How it works
The application saves a JSON file in the selected directory with the name of the repeater tab, using the following format:
````
{
    "request": {request enconded in base64},
    "tabName": {repeater tab name}, 
    "protocol": {protocol}, 
    "port": {port}, 
    "response": {response enconded in base64}, 
    "host": {host}
}
````
