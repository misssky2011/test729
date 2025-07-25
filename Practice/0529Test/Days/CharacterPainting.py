from PIL import Image

# ASCII characters to use for the art
ASCII_CHARS = ['@', '#', 'S', '%', '?', '*', '+', ';', ':', ',', '.']

# Resizing the image
def resize_image(image, new_width=100):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image

# Convert image to grayscale
def grayify(image):
    return image.convert("L")

# Convert each pixel to an ASCII character
def pixels_to_ascii(image):
    pixels = image.getdata()
    ascii_str = ''
    for pixel in pixels:
        ascii_str += ASCII_CHARS[pixel // 25]  # Dividing by 25 to map pixel values to the ASCII_CHAR index
    return ascii_str

# Main function to convert the image to ASCII art
def image_to_ascii(image_path, new_width=100):
    try:
        image = Image.open(image_path)
    except Exception as e:
        print(e)
        return

    image = resize_image(image)
    image = grayify(image)

    ascii_str = pixels_to_ascii(image)
    img_width = image.width
    ascii_str_len = len(ascii_str)
    ascii_img = ''

    # Break the ASCII string into multiple lines based on the image width
    for i in range(0, ascii_str_len, img_width):
        ascii_img += ascii_str[i:i+img_width] + '\n'

    return ascii_img

if __name__ == '__main__':
    image_path = input("Enter the image path: ")
    ascii_image = image_to_ascii(image_path)
    if ascii_image:
        print(ascii_image)
        # Optionally, save the ASCII art to a file
        with open("../ascii_art.txt", "w") as f:
            f.write(ascii_image)
