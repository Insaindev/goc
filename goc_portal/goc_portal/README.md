# youtube source https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=WL&index=1&t=181s

# source github https://github.com/CoreyMSchafer/code_snippets/blob/master/Python/Flask_Blog/08-Posts/flaskblog/routes.py

# github git clone https://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@github.com/Insaindev/memorise_v2.git


#youtube annia https://www.youtube.com/watch?v=i6qL3NqFjs4

chatgpt otazka pre navrh designu
python web application which allow to upload text file. html layout for main form is on left side vertical main menu, in center empty block prepared for list of items. After click on main menu item button open new vertical submenu with options such as insert, edit, delete. After click to insert button modal window show with required input 2 fields and submit button 



from zipfile import ZipFile

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']
    if file.filename == '':
        return 'No selected file'

    if file and file.filename.endswith('.zip'):
        with ZipFile(file, 'r') as zip:
            zip.extractall()
            for name in zip.namelist():
                with open(name, 'r') as f:
                    print(f.read())
            return 'Zip file uploaded and unzipped successfully'
    else:
        return 'Invalid file type'