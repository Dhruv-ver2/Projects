import string

def process_text(text, shift, mode):
    """
    Encrypts or decrypts text using the Caesar cipher in a single function.
    
    :param text: The input string.
    :param shift: The integer key for the shift.
    :param mode: A string, either 'encrypt' or 'decrypt'.
    :return: The processed string.
    """
    # If in decrypt mode, just reverse the shift
    if mode == 'decrypt':
        shift = -shift
        
    result = ''
    alpha = string.ascii_uppercase

    for char in text:
        char_upper = char.upper()
        if char_upper in alpha:
            p = alpha.find(char_upper)
            # The formula now works for both modes!
            np = (p + shift) % 26
            result += alpha[np]
        else:
            result += char
            
    return result

# --- Let's run it ---

# Setup
original_message = "Meet in Daulatganj"
key = 7

# Encrypt
print(f"Original Message:  {original_message}")
encrypted = process_text(original_message, key, 'encrypt')
print(f"Encrypted Message: {encrypted.lower()}")

# Decrypt using the same function, just changing the mode
decrypted = process_text(encrypted, key, 'decrypt')
print(f"Decrypted Message: {decrypted.lower()}")

print("Program Completed by here")
exit()