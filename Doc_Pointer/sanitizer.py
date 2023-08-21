import re
import sys

def get_replacement_dictionary():
    return {
        ## Empty replacements
        '.': '',
        ':': '',
        ';': '',
        ',': '',
        ')': '',
        '(': '',
        '!': '',
        '"': '',
        '“': '',
        '§': '',
        '$': '',
        '%': '',
        '&': '',
        '/': '',
        '=': '',
        '?': '',
        '{': '',
        '}': '',
        '[': '',
        ']': '',
        '0': '',
        '1': '',
        '2': '',
        '3': '',
        '4': '',
        '5': '',
        '6': '',
        '7': '',
        '8': '',
        '9': '',
        '•': '',
        '°': '',
        '″': '',
        '′': '',
        '°c': '',
        '°f': '',
        '−': '',
        '≥': '',
        '±': '',
        '–': '',
        '€': '',
        '·': '',
        '⬤': '',
        '½': '',
        '\'': '',
        '‘': '',
        '!': '',
        '…': '',
        '£': '',
        '⁄': '',
        '√': '',
        '@': '',
        '✓': '',
        '¡': '',
        '🇮🇸🇮🇸': '',
        '🇳🇴': '',
        '^': '',
        '|': '',
        '∩': '',
        '☾': '',
        '🇦🇪': '',
        '🇦🇹': '',
        '🇧🇪': '',
        '🇧🇪': '',
        '🇧🇪': '',
        '🇨🇦': '',
        '🇨🇭': '',
        '🇩🇪': '',
        '🇩🇪🇩🇪': '',
        '🇩🇰': '',
        '🇫🇮': '',
        '🇫🇷': '',
        '🇬🇧': '',
        '🇮🇩': '',
        '🇮🇪': '',
        '🇮🇸': '',
        '🇳🇬': '',
        '🇳🇱': '',
        '🇳🇴': '',
        '🇳🇿': '',
        '🇵🇹': '',
        '🇺🇦🇺🇦🇺🇦': '',
        '🇺🇸': '',
        '🇺🇸🇺🇸': '',
#        '🇦🇺': '',
#        '🇮🇳': '',
#        '🇵🇷': '',
#        '🇸🇬': '',
#        '🇵🇷': '',
#        '🇺🇦': '',
        '♫': '',
        '←': '',
        '’': '',
        '✓✓✓': '',
#        '🇧🇷': '',
#        '\\': '',
#        '’': '',
#        '⌒ヽ': '',
#        'ヽ': '',
#        '²': '',
        ## Space replacements
        '+': ' ',
        '-': ' ',
        '~': ' ',
        '#': ' ',
        '*': ' ',
        '—': ' ',
        '_': ' ',
        '<': ' ',
        '>': ' ',
        '\n': ' ',
        "'s": ' ',
        "’s": ' ',
        "'nt": ' ',
        " nt ": ' ',
        "'th": ' ',
        " th ": ' ',
        "'st": ' ',
        " st ": ' ',
        "”": ' ',
        "'nd": ' ',
        " nd ": ' ',
        "ː": ""}

if __name__ == "__main__":
    file_to_parse = sys.argv[1]
    filename_to_parse = file_to_parse.split('/')[-1].split('.')[0]
    output_dir = sys.argv[2]


    transition_dictionary = get_replacement_dictionary()

    regex_rules = re.compile("(%s)" % "|".join(map(re.escape, transition_dictionary.keys())))


    text_to_sanitize = open(file_to_parse, 'r').read().lower()

    sanitized_text_with_spaces = regex_rules.sub(lambda mo: transition_dictionary[mo.string[mo.start():mo.end()]], text_to_sanitize)
    sanitized_text = " ".join(re.sub(' +', ' ', sanitized_text_with_spaces).split())

    with open(output_dir+'/san_' + filename_to_parse + '.txt','w') as out:
        out.write(sanitized_text)