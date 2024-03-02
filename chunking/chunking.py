from solon_tokenization import tokenize
import json
import re

''' MAKE SURE TO HAVE THE MICROU.JSON FILE READY'''

MAX_TOKENS = 480    # Maximum number of tokens per chunk (technically 512, but we want to leave some headroom incase splitting actually increases the token count)

def check_tokens(text):
    tokens = tokenize(text)
    return len(tokens)

def group_chunks(chunks, min_tokens=0, max_tokens=MAX_TOKENS, type="paragraph"):
    """
    Groups chunks of text into lists such that each list has a total token count less than or equal to max_tokens whilst minimizing the number of groups.
    warning: setting min_tokens to a value greater than 0 may result in dropping tokens if there is no optimal grouping.

    TODO: for section grouping, prevent grouping an orphan portion of a section of a given level with the previous section of the same level (you don't
    want to have only the title of a section in a previous one, and the content in the next one)
    """
    n = len(chunks)
    last_index=[-1]*n
    dp=[float('inf')]*(n+1)

    # Initialization
    dp[0] = 1 if chunks[0][0] <= max_tokens and chunks[0][0] >= min_tokens else float('inf')
    last_index[0] = 0  if dp[0] == 1 else -1 # First list starts the first group 
    
    for i in range(1, n):
        current_size = 0
        for j in range(i, -1, -1):
            current_size += chunks[j][0]
            if current_size > max_tokens or (i - j > 0 and current_size < min_tokens):
                break
            if j == 0 and current_size >= min_tokens:
                dp[i] = 1
                last_index[i] = 0
            elif current_size >= min_tokens:
                if dp[j-1] + 1 < dp[i]:
                    dp[i] = dp[j-1] + 1
                    last_index[i] = j  # Update lastIndex for tracking
    
    # Reconstruct the groups
    groups = []
    index = len(last_index) - 1
    while index >= 0:
        group_start = last_index[index]
        if group_start == -1:  # Skip if not a valid start
            index -= 1
            continue

        # handle different types of grouping (new line if sections, concatenation if paragraphs)
        if type=="section":
            group = "  \n".join([chunks[chunk][1] for chunk in range(group_start,index+1)])
        else:
            group = " ".join([chunks[chunk][1] for chunk in range(group_start,index+1)])
        
        groups.append(group)
        index = group_start - 1
    groups.reverse()  # Reverse to get the original order
    # print(groups)
    return groups

def split_into_sentences(text, max_tokens=MAX_TOKENS):
    """
    Splits a paragraph into sentences.
    """
    pattern = r'(?<!\w\.\w.)((?<!\s[A-Z].)|(?<!\s[A-Z][a-z]\.)|(?<!\s[A-Z][a-z][a-z]\.))(?<=\.|\?|!|:)\s'
    sentences = re.split(pattern, text)
    # Filter out any empty strings
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

    text_breakdown=[]
    for sentence in sentences:
        print(sentence)
        sentence_size=check_tokens(sentence)
        text_breakdown.append([sentence_size,sentence])
    
    consolidated_sentences=group_chunks(text_breakdown)

    # unlike paragraphs and sections, the output will never be processed again so it has to be in final form
    consolidated_sentences=[[check_tokens(sentence),sentence] for sentence in consolidated_sentences]
    
    return consolidated_sentences

def split_into_paragraphs(text, max_tokens=MAX_TOKENS):
    """
    Splits a markdown document into paragraphs.
    """
    pattern = r'\n'
    paragraphs = re.split(pattern, text)
    # Filter out any empty strings
    paragraphs = [paragraph.strip() for paragraph in paragraphs if paragraph.strip()]

    text_breakdown=[]
    for paragraph in paragraphs:
        paragraph_size=check_tokens(paragraph)
        if paragraph_size>max_tokens:
            text_breakdown.extend(split_into_sentences(paragraph))
        else:
            text_breakdown.append([paragraph_size,paragraph])

    consolidated_paragraphs=group_chunks(text_breakdown)

    return consolidated_paragraphs

def split_into_sections(text, level=None, max_tokens=MAX_TOKENS):
    """
    Splits a markdown document into sections based on headings up to a specified level.
    """

    # If no level is specified, split the document into paragraphs
    if level is None:
        sections = split_into_paragraphs(text)

    else:
        # Pattern to match headings up to the specified level
        pattern = rf'(^|\n){"#"*level} .+?\n'

        # Find all matches and collect start positions
        # print([match.group() for match in re.finditer(pattern, text, re.MULTILINE)])
        starts=[match.start() for match in re.finditer(pattern, text, re.MULTILINE)]
        
        # insert 0 at the beginning if the first section is not at the beginning of the text
        if len(starts)!=0 and starts[0]!=0:
            starts.insert(0,0)

        # Add the end of the text as the final 'start' to capture the last section
        starts.append(len(text))
        
        # Use start positions to split the text into chunks
        sections = [text[starts[i]:starts[i+1]] for i in range(len(starts)-1)]
        
        # Filter out any empty strings
        sections = [section.strip() for section in sections if section.strip()]

        # If no sections were founds because the level was too high, then look for lists    
        if len(sections) == 0:
            level = None
            ul_pattern = r'(^|\n)- .+?\n'
            ol_pattern = r'(^|\n)\d+\. .+?\n'
            ul_starts = [match.start() for match in re.finditer(ul_pattern, text, re.MULTILINE)]
            ol_starts = [match.start() for match in re.finditer(ol_pattern, text, re.MULTILINE)]
            ul_starts.append(len(text))
            ol_starts.append(len(text))

            if ul_starts[0]==ol_starts[0]: #can only happen if there are no lists so the first element is the end of the text
                sections = split_into_paragraphs(text)
            
            else:
                starts=[0]
                if ul_starts[0]<ol_starts[0]:
                    starts.extend(ul_starts)
                else:
                    starts.extend(ol_starts)
                
                # Use start positions to split the text into chunks
                sections = [text[starts[i]:starts[i+1]] for i in range(len(starts)-1)]
                
                # Filter out any empty strings
                sections = [section.strip() for section in sections if section.strip()]
        else:
            level = level+1

    text_breakdown=[]
    for section in sections:
        section_size=check_tokens(section)
        if section_size>max_tokens:
            text_breakdown.extend(split_into_sections(section,level))
        else:
            text_breakdown.append([section_size,section])

    return text_breakdown


if __name__ == "__main__":
    with open('./microu.json', 'r') as f:
        data = json.load(f)

        total_chunks = 0

    # Tokenize the text
        for i in range(len(data)):# len(data)
            print("Document ",i, data[i]['titre'])
            document=data[i]
            contenu=document['contenu']
            contenu_size=check_tokens(contenu)
            sections=split_into_sections(contenu,1)
            sections=group_chunks(sections, type="section")
            total_tokens=0
            chunks=[]
            for j in range(len(sections)):
                section_length=check_tokens(sections[j])
                # print(section_length," --- ",sections[j])
                chunks.append({'tokens':section_length,'chunk':sections[j]})
                total_tokens+=section_length
            document['total_chunks']=len(sections)
            document['chunks']=chunks
            document['total_tokens']=total_tokens
            document['taille_contenu']=contenu_size
            total_chunks+=len(sections)
            if total_tokens<=contenu_size:
                print("Warning : Total tokens: ",total_tokens, " vs. Contenu size: ",contenu_size)
                print("-------------------")

        print("Total chunks: ",total_chunks)

    with open('microu-chunked.json', 'w') as f:
        json.dump(data, f, indent=4) 