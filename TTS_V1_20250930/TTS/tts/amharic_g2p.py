import re
G2P_MAP = {
    'ሀ': 'hə', 'ሁ': 'hu', 'ሂ': 'hi', 'ሃ': 'ha', 'ሄ': 'he', 'ህ': 'hɨ', 'ሆ': 'ho',
    'ለ': 'lə', 'ሉ': 'lu', 'ሊ': 'li', 'ላ': 'la', 'ሌ': 'le', 'ል': 'lɨ', 'ሎ': 'lo', 'ሏ': 'lwa',
    'ሐ': 'ha', 'ሑ': 'hu', 'ሒ': 'hi', 'ሓ': 'ha', 'ሔ': 'he', 'ሕ': 'hɨ', 'ሖ': 'ho', 'ሗ': 'hwa',
    'መ': 'mə', 'ሙ': 'mu', 'ሚ': 'mi', 'ማ': 'ma', 'ሜ': 'me', 'ም': 'mɨ', 'ሞ': 'mo', 'ሟ': 'mwa',
    'ሠ': 'sə', 'ሡ': 'su', 'ሢ': 'si', 'ሣ': 'sa', 'ሤ': 'se', 'ሥ': 'sɨ', 'ሦ': 'so', 'ሧ': 'swa',
    'ረ': 'rə', 'ሩ': 'ru', 'ሪ': 'ri', 'ራ': 'ra', 'ሬ': 're', 'ር': 'rɨ', 'ሮ': 'ro', 'ሯ': 'rwa',
    'ሰ': 'sə', 'ሱ': 'su', 'ሲ': 'si', 'ሳ': 'sa', 'ሴ': 'se', 'ስ': 'sɨ', 'ሶ': 'so', 'ሷ': 'swa',
    'ሸ': 'ʃə', 'ሹ': 'ʃu', 'ሺ': 'ʃi', 'ሻ': 'ʃa', 'ሼ': 'ʃe', 'ሽ': 'ʃɨ', 'ሾ': 'ʃo', 'ሿ': 'ʃwa',
    'ቀ': 'kʼə', 'ቁ': 'kʼu', 'ቂ': 'kʼi', 'ቃ': 'kʼa', 'ቄ': 'kʼe', 'ቅ': 'kʼɨ', 'ቆ': 'kʼo', 'ቋ': 'kʼwa',
    'ቐ': 'kʼə', 'ቑ': 'kʼu', 'ቒ': 'kʼi', 'ቓ': 'kʼa', 'ቔ': 'kʼe', 'ቕ': 'kʼɨ', 'ቖ': 'kʼo',
    'በ': 'bə', 'ቡ': 'bu', 'ቢ': 'bi', 'ባ': 'ba', 'ቤ': 'be', 'ብ': 'bɨ', 'ቦ': 'bo', 'ቧ': 'bwa',
    'ቨ': 'və', 'ቩ': 'vu', 'ቪ': 'vi', 'ቫ': 'va', 'ቬ': 've', 'ቭ': 'vɨ', 'ቮ': 'vo', 'ቯ': 'vwa',
    'ተ': 'tə', 'ቱ': 'tu', 'ቲ': 'ti', 'ታ': 'ta', 'ቴ': 'te', 'ት': 'tɨ', 'ቶ': 'to', 'ቷ': 'twa',
    'ቸ': 'tʃä', 'ቹ': 'tʃu', 'ቺ': 'tʃi', 'ቻ': 'tʃa', 'ቼ': 'tʃe', 'ች': 'tʃɨ', 'ቾ': 'tʃo', 'ቿ': 'tʃwa',
    'ኀ': 'ħä', 'ኁ': 'ħu', 'ኂ': 'ħi', 'ኃ': 'ħa', 'ኄ': 'ħe', 'ኅ': 'hɨ', 'ኆ': 'ħo', 'ኋ': 'hwa',
    'ነ': 'nə', 'ኑ': 'nu', 'ኒ': 'ni', 'ና': 'na', 'ኔ': 'ne', 'ን': 'nɨ', 'ኖ': 'no', 'ኗ': 'nwa',
    'ኘ': 'ɲä', 'ኙ': 'ɲu', 'ኚ': 'ɲi', 'ኛ': 'ɲa', 'ኜ': 'ɲe', 'ኝ': 'ɲɨ', 'ኞ': 'ɲo', 'ኟ': 'ɲwa',
    'አ': 'ʔə', 'ኡ': 'ʔu', 'ኢ': 'ʔi', 'ኣ': 'ʔa', 'ኤ': 'ʔe', 'እ': 'ʔɨ', 'ኦ': 'ʔo',
    'ከ': 'kə', 'ኩ': 'ku', 'ኪ': 'ki', 'ካ': 'ka', 'ኬ': 'ke', 'ክ': 'kɨ', 'ኮ': 'ko', 'ኰ': 'kwə', 'ኳ': 'kwa',
    'ኸ': 'xä', 'ኹ': 'xu', 'ኺ': 'xi', 'ኻ': 'xa', 'ኼ': 'xe', 'ኽ': 'x', 'ኾ': 'xo',
    'ወ': 'wə', 'ዉ': 'wu', 'ዊ': 'wi', 'ዋ': 'wa', 'ዌ': 'we', 'ው': 'wɨ', 'ዎ': 'wo',
    'ዐ': 'ʕä', 'ዑ': 'ʕu', 'ዒ': 'ʕi', 'ዓ': 'ʕa', 'ዔ': 'ʕe', 'ዕ': 'ʕɨ', 'ዖ': 'ʕo',
    'ዘ': 'zə', 'ዙ': 'zu', 'ዚ': 'zi', 'ዛ': 'za', 'ዜ': 'ze', 'ዝ': 'zɨ', 'ዞ': 'zo', 'ዟ': 'zwa',
    'ዠ': 'ʒə', 'ዡ': 'ʒu', 'ዢ': 'ʒi', 'ዣ': 'ʒa', 'ዤ': 'ʒe', 'ዥ': 'ʒɨ', 'ዦ': 'ʒo', 'ዧ': 'ʒwa',
    'የ': 'jə', 'ዩ': 'ju', 'ዪ': 'ji', 'ያ': 'ja', 'ዬ': 'je', 'ይ': 'jɨ', 'ዮ': 'jo',
    'ደ': 'də', 'ዱ': 'du', 'ዲ': 'di', 'ዳ': 'da', 'ዴ': 'de', 'ድ': 'dɨ', 'ዶ': 'do', 'ዷ': 'dwa',
    'ጀ': 'dʒä', 'ጁ': 'dʒu', 'ጂ': 'dʒi', 'ጃ': 'dʒa', 'ጄ': 'dʒe', 'ጅ': 'dʒɨ', 'ጆ': 'dʒo', 'ጇ': 'dʒwa',
    'ገ': 'ɡə', 'ጉ': 'gu', 'ጊ': 'gi', 'ጋ': 'ga', 'ጌ': 'ge', 'ግ': 'ɡɨ', 'ጎ': 'go', 'ጐ': 'ɡwə',
    'ጠ': 'tʼə', 'ጡ': 'tʼu', 'ጢ': 'tʼi', 'ጣ': 'tʼa', 'ጤ': 'tʼe', 'ጥ': 'tʼɨ', 'ጦ': 'tʼo', 'ጧ': 'tʼwa',
    'ጨ': 'tʃʼə', 'ጩ': 'tʃʼu', 'ጪ': 'tʃʼi', 'ጫ': 'tʃʼa', 'ጬ': 'tʃʼe', 'ጭ': 'tʃʼɨ', 'ጮ': 'tʃʼo', 'ጯ': 'tʃʼwa',
    'ጸ': 'sʼə', 'ጹ': 'sʼu', 'ጺ': 'sʼi', 'ጻ': 'sʼa', 'ጼ': 'sʼe', 'ጽ': 'sʼɨ', 'ጾ': 'sʼo', 'ጿ': 'sʼwa',
    'ጰ': 'pʼə', 'ጱ': 'pʼu', 'ጲ': 'pʼi', 'ጳ': 'pʼa', 'ጴ': 'pʼe', 'ጵ': 'pʼɨ', 'ጶ': 'pʼo', 'ጷ': 'pʼwa',
    'ፀ': 'sʼə', 'ፁ': 'sʼu', 'ፂ': 'sʼi', 'ፃ': 'sʼa', 'ፄ': 'sʼe', 'ፅ': 'sʼɨ', 'ፆ': 'sʼo',
    'ፈ': 'fə', 'ፉ': 'fu', 'ፊ': 'fi', 'ፋ': 'fa', 'ፌ': 'fe', 'ፍ': 'fɨ', 'ፎ': 'fo', 'ፏ': 'fwa',
    'ፐ': 'pə', 'ፑ': 'pu', 'ፒ': 'pi', 'ፓ': 'pa', 'ፔ': 'pe', 'ፕ': 'p', 'ፖ': 'po', 'ፗ': 'pwa'
}

# amharic_number_g2p_full.py

UNITS = {
    1: 'ʔänd',
    2: 'hulätt',
    3: 'sost',
    4: 'arät',
    5: 'äməst',
    6: 'səddɨst',
    7: 'säbat',
    8: 'səmɨnt',
    9: 'zätʼäñ'
}

TENS = {
    10: 'ʔäśɨr',
    20: 'häyɨ',
    30: 'sälsa',
    40: 'arbä',
    50: 'hämʃä',
    60: 'säḱsä',
    70: 'säbʕä',
    80: 'sämanä',
    90: 'zätʼäñä'
}

HUNDRED = 'mäto'
THOUSAND = 'ʃi'
MILLION = 'milɨyon'

def convert_below_1000(n):
    parts = []
    h = n // 100
    t = (n % 100) // 10 * 10
    u = n % 10

    if h:
        parts.append(UNITS[h])
        parts.append(HUNDRED)

    if t:
        parts.append(TENS[t])
        if u:
            parts.append(UNITS[u])
    elif u:
        parts.append(UNITS[u])

    return " ".join(parts)

def number_to_amharic_ipa(n: int) -> str:
    if n < 1 or n > 100_000_000:
        raise ValueError("Only numbers from 1 to 100,000,000 are supported.")

    if n == 100_000_000:
        return f"{UNITS[1]} {MILLION} {UNITS[100]} {THOUSAND}"

    result = []

    millions = n // 1_000_000
    thousands = (n % 1_000_000) // 1_000
    below_thousand = n % 1000

    if millions:
        if millions == 1:
            result.append(UNITS[1])
        else:
            result.append(convert_below_1000(millions))
        result.append(MILLION)

    if thousands:
        if thousands == 1:
            result.append(UNITS[1])
        else:
            result.append(convert_below_1000(thousands))
        result.append(THOUSAND)

    if below_thousand:
        result.append(convert_below_1000(below_thousand))

    return " ".join(result).strip()
import re

def g2p_amharic(text: str) -> str:
    """
    Convert Amharic text to phoneme-like string using G2P map and number handler.
    Preserves spaces between words, not between every phoneme.
    """
    words = text.split()
    output_words = []
    for word in words:
        tokens = re.findall(r'\d+|.', word)  # keep digits as blocks, otherwise single chars
        phonemes = []
        for token in tokens:
            if token.isdigit():
                try:
                    phonemes.append(number_to_amharic_ipa(int(token)))
                except ValueError:
                    phonemes.append(token)
            else:
                phonemes.append(G2P_MAP.get(token, token))
        # join phonemes without spaces inside a word
        output_words.append("".join(phonemes))
    # join words with spaces
    return " ".join(output_words)



