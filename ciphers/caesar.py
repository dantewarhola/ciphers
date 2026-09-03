#Caesar cipher encoder / decoder with input validation.


# Shift every letter by key. Input is validated upstream
# So the final branch only ever sees spaces.
def shift_text(plaintext, key):
    output = ""
    for char in plaintext:
        if char.isupper():
            output += chr((ord(char) - 65 + key) % 26 + 65)
        elif char.islower():
            output += chr((ord(char) - 97 + key) % 26 + 97)
        else:
            output += char
    return output


def encrypt_text(plaintext, key):
    return shift_text(plaintext, key)
 
 
def decrypt_text(plaintext, key):
    return shift_text(plaintext, -key)


def brute_force_decrypt(plaintext):
    i = 1
    print("\nThese are all possible decryptions:")
    print("--------------------------------------------")
    while i < 26:
        answer = print("Key = " + str(i) + ": " + shift_text(plaintext, -i))
        i += 1
    return answer


# True for A-Z, a-z, and the space character. Everything else is rejected.
def is_allowed(char):
    return char == " " or (char.isascii() and char.isalpha())


# Keep asking until the user gives us letters and spaces only.
def get_text(prompt):
    while True:
        plaintext = input(prompt)
 
        if not plaintext.strip():
            print("Input can't be empty. Try again.\n")
            continue
 
        rejected = sorted({char for char in plaintext if not is_allowed(char)})
        if rejected:
            shown = " ".join(repr(char) for char in rejected)
            print(f"Letters and spaces only. Remove these: {shown}\n")
            continue
 
        return plaintext


# Keep asking until the user gives us a whole number.
def get_key(prompt):
    while True:
        raw = input(prompt).strip()
        try:
            return int(raw)
        except ValueError:
            print(f"'{raw}' isn't a whole number. Enter something like 3 or -5.\n")


def run_cipher(mode):
    if mode == "encode":
        plaintext = get_text("Enter plaintext: ")
        key = get_key("Enter key: ")
        print(f"\nYour encrypted text is: {encrypt_text(plaintext, key)}")
    elif mode == "decode":
        plaintext = get_text("Enter ciphertext: ")
        key = get_key("Enter key: ")
        print(f"\nYour plaintext is: {decrypt_text(plaintext, key)}")
    elif mode == "brute_force":
        plaintext = get_text("Enter ciphertext: ")
        brute_force_decrypt(plaintext)
    print("--------------------------------------------\n")






def main():
    print()
    print("Welcome to Caesar Cipher Encoding & Decoding")
    while True:
        print("What would you like to do?")
        print("1: Encode")
        print("2: Decode W/ Key")
        print("3: Brute Force Decode")
        print("Q: Quit")
        print("--------------------------------------------")
 
        try:
            answer = input("Choice: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            print("--------------------------------------------")
            return
 
        if answer in ("quit", "q", "Q"):
            print("\nGoodbye!")
            print("--------------------------------------------")
            return
        elif answer == "1":
            run_cipher("encode")
        elif answer == "2":
            run_cipher("decode")
        elif answer == "3":
            run_cipher("brute_force")
        else:
            print(f"\n'{answer}' isn't an option. Pick 1, 2, or Q.\n")
 
 
if __name__ == "__main__":
    main()