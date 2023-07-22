import json
import pypandoc
import zipfile
import os

# Import a latex file with pandoc
input_data = pypandoc.convert_file('data/example.tex', 'json')

# Parse the pandoc JSON output into Python
parsed_data=json.loads(input_data)


# Function that processes maths content
def extract_math_content(elem):
    if elem['t'] == 'Math':
        if elem['c'][0]['t'] == 'InlineMath':
            return '$' + elem['c'][1] + '$'
        elif elem['c'][0]['t'] == 'DisplayMath':
            print(elem)
            return '$$' + elem['c'][1] + '$$'
    return ''

# Function that processes normal content
def content_extractor(par):
    markdown = ''
    if par['c'][0]['t'] == 'Str':                   
        content = par['c']                        
        for elem in content:
            if elem['t'] == 'Str':
                markdown += elem['c']
            elif elem['t'] == 'Math':
                markdown += '$' + elem['c'][1] + '$'
            elif elem['t'] == 'Space':
                markdown += ' '
        converted = pypandoc.convert_text(markdown, 'markdown', format='markdown')
        return converted
    elif par['c'][0]['t'] == 'Math':                      
        content = par['c']
        markdown = '$$' + par['c'][0]['c'][1] + '$$'
        converted = pypandoc.convert_text(markdown, 'markdown', format='markdown')
        return converted
    else:
        return ''

def converter(template):
    # Loop through the blocks in the content until an 'orderedlist' is found. This is specific to the way the example latex file is created, using \begin{enumerate}
    for block in parsed_data['blocks']:
        if block['t']=='OrderedList':
            block_lists = block['c'][1:]                                                    # Ignore [0] as a header, go from [1] onwards
            for block_list in block_lists:
                for i,question in enumerate(block_list):                                    # The JSON structure has another layer of nesting
                    #print('Q'+str(i+1)+'\n\n')                                              # Printing for demo purposes only
                    lambda_output=template
                    output = ''
                    for j,par in enumerate(question):                                       # Question content is composed of multiple elements (paragraphs, maths, lists, etc.)
                        if par['t']=='Para':                                                # Normal paragraphs i.e. for master content                               
                            output += content_extractor(par)  # Write to JSON master content here
                        elif par['t']=='OrderedList':
                            par_lists = par['c'][1:]                                        # List in a list for parts of a questions (part (a), (b), etc.)
                            for par_list in par_lists:
                                for k,part in enumerate(par_list):
                                    # This part does convert, but isn't written to the JSON yet (unfinished work)
                                    print()
                                    #print('Q'+str(i+1)+'('+chr(k+ord('a'))+')\n\n')
                                    #This is the part to change: template['parts'][j]['content']['blocks'][0]['data']='bvlah'
                                    #output += content_extractor(part[0])
                                    #print(output)                                           # Write to JSON part content here
                                    #print('\n\n')
                    lambda_output['masterContent']['blocks'][0]['data']=output
                    subdir='outputs'
                    os.makedirs(subdir, exist_ok=True)
                    filepath_j=os.path.join(subdir,'Q'+str(i+1)+'.json')
                    filepath_z=os.path.join(subdir,'Q'+str(i+1)+'.zip')
                    with open(filepath_j,'w') as file:
                        json.dump(lambda_output,file) 
                    with zipfile.ZipFile(filepath_z, "w") as zipf:
                        zipf.write(filepath_j, arcname=filepath_j)

# Main code
def main():
    with open("data/minimal_template.json", "r") as file:
        template = json.load(file)
    converter(template)

if __name__ == '__main__':
    main()