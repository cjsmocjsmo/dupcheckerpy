import os


class ExtCount:
    def __init__(self, folder):
        # image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        self.pngcount = 0
        self.jpgcount = 0
        self.jpegcount = 0
        self.gifcount = 0
        self.bmpcount = 0
        self.count3gp = 0
        self.jsoncount = 0
        self.pdfcount = 0
        self.mp4count = 0
        self.folder = folder
        self.ext_list = []

    def get_ext_count(self):
        for dir, _, files in os.walk(self.folder):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                self.ext_list.append(ext)
                fpath = os.path.join(dir, file)

                if file.lower().endswith(".png"):
                    self.pngcount += 1
                    print(file)
                elif file.lower().endswith(".jpg"):
                    self.jpgcount += 1
                elif file.lower().endswith(".jpeg"):
                    self.jpegcount += 1
                elif file.lower().endswith(".gif"):
                    self.gifcount += 1
                elif file.lower().endswith(".bmp"):
                    self.bmpcount += 1
                elif file.lower().endswith(".mp4"):
                    self.mp4count += 1
                elif file.lower().endswith(".3gp"):
                    self.count3gp += 1
                    print(fpath)
                elif file.lower().endswith(".json"):
                    self.jsoncount += 1
                elif file.lower().endswith(".pdf"):
                    self.pdfcount += 1


        print(f"PNG: {self.pngcount}")
        print(f"JPG: {self.jpgcount}")
        print(f"JPEG: {self.jpegcount}")
        print(f"GIF: {self.gifcount}")
        print(f"BMP: {self.bmpcount}")
        print(f"MP4: {self.mp4count}")
        print(f"3GP: {self.count3gp}")
        print(f"JSON: {self.jsoncount}")
        print(f"PDF: {self.pdfcount}")
        print(f"ext_list: {list(set(self.ext_list))}")


if __name__ == '__main__':
    folder = '/home/whitepi/Pictures'
    ext_counter = ExtCount(folder).get_ext_count()