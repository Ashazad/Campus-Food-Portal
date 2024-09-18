from PIL import Image

image = Image.open("static/images/dish3.png")
new_image = image.resize((50, 50))
new_image.save("dish3.png")