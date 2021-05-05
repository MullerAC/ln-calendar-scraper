"""
TODO
add methods useful for scraping and posting data:
- run all scrapers and compile into pandas dataframe
- add MAL links from archive
- check for broken links (any) or missing store links
- print out pandas dataframe into reddit markup
- pull existing table from Reddit wiki and run a compare
- post to staging wiki
"""

def get_format(format_input):
    physical_words = ['hardcover', 'hc', 'paperback', 'physical', 'tpb']
    digital_words = ['digital', 'ebook', 'epub', 'mobi', 'pdf']
    audio_words = ['audio', 'audiobook']

    physical = any(word.casefold() in format_input.casefold() for word in physical_words)
    digital = any(word.casefold() in format_input.casefold() for word in digital_words)
    audio = any(word.casefold() in format_input.casefold() for word in audio_words)

    format_output = []
    if physical:
        format_output += 'Physical'
    if digital:
        format_output += 'Digital'
    if audio:
        format_output += 'Audio'
    
    if not format_output:
        print('Could not find format for: ', format_input)
        return 'Other'
    else:
        return ' & '.join(format_output)
