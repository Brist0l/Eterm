# Eterm

Send Emails through the terminal , fast and secure

## Installation

Use git to install it

```bash
git clone https://github.com/mrHola21/Eterm.git
```

## Usage

```bash
cd eterm/src
```

This example over here sends an email with a body , subject and a file:

```bash
python3 main.py {from_email} --to {to_email} --body --subject --file {files}
```

Note : You can send multiple files too just by specifying the files after the file.


For help:

```bash
python3 main.py -h
```

## Features

1) Autocompletions
2) Secure , it has got a sha512 hash implemented and when typing the password ,the password is not visible
3) feature rich , You can send files too

## Autocompletion

To add autocompletion add the phrases and Locations in Autocompletions/files.txt and greeting. eg. in the files.txt you
can add a folder name in which you have kept all the documents you want to email someone, you can specify the folder .

```text
/home/foo/Documents/stuff
```

## Using Autocompletion
To use autocompletion just press the `tab` key

## 10 reasons to use it 

1) It's easy to use 
2) It's fast
3) It's secure
4) Autocompletions
5) Stores autocompletion history for fast access
6) It's Lightweight
7) When sending attachments , the name of the attachment is also displayed
8) It's pretty
9) Be a terminal geek
10) Configurable SMTP 

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[GNU GPL v3](https://choosealicense.com/licenses/gpl-3.0/)
