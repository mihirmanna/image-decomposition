import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image


class Quadtree:
    def __init__(self, boundary, plot, image):
        self.boundary = boundary
        self.plot = plot
        self.image = image
        
        self.northeast = None
        self.northwest = None
        self.southwest = None
        self.southeast = None
        
        self.has_divided = False
        
    def subdivide(self):
        """
        Divides this cell into four smaller cells and adds them as children of this one
        """
        x = self.boundary.get_x()
        y = self.boundary.get_y()
        w = self.boundary.get_width()
        h = self.boundary.get_height()
        
        # Boundaries for quadrants
        ne = Rectangle((x + w/2, y + h/2), w/2, h/2)
        nw = Rectangle((x, y + h/2), w/2, h/2)
        sw = Rectangle((x, y), w/2, h/2)
        se = Rectangle((x + w/2, y), w/2, h/2)
        
        self.northeast = Quadtree(ne, self.plot, self.image)
        self.northwest = Quadtree(nw, self.plot, self.image)
        self.southwest = Quadtree(sw, self.plot, self.image)
        self.southeast = Quadtree(se, self.plot, self.image)
        
        self.has_divided = True
    
    def draw(self):
        """
        Draws a rectangle corresponding to this cell's boundary
        whose color is the average of uniformly sampled pixels from the cell
        """
        avg_color = self.average_color()
        self.boundary.set_facecolor([i/255 for i in avg_color])
        self.plot.add_patch(self.boundary)
        
        if self.has_divided:
            self.northeast.draw()
            self.northwest.draw()
            self.southwest.draw()
            self.southeast.draw()
    
    def sample_pixel_colors(self, step):
        """
        Takes a uniform sample of pixel colors from this cell
        
        :param step: The distance between pixels in the sample
        :return: A list of the pixel colors in hexadecimal form
        """
        pix = self.image.load()
        pix_list = []

        # Store hex colors of uniformly sampled pixels in this quadrant
        x = int(self.boundary.get_x())
        y = int(self.boundary.get_y())
        w = int(self.boundary.get_width())
        h = int(self.boundary.get_height())
        for i in range(x, x+w, step):
            for j in range(y, y+h, step):
                pix_list.append(pix[i, j][0:3])  # Only use RGB values (ignore alpha)

        return pix_list

    def average_color(self):
        """
        Determines the average color of this cell using the RGB channels from a sample of pixels

        :return: The average color as a tuple [R, G, B]
        """
        pixels = self.sample_pixel_colors(25)
        red, green, blue = [], [], []

        for i in pixels:
            red.append(i[0])
            green.append(i[1])
            blue.append(i[2])
            
        avg_color = [np.mean(red), np.mean(green), np.mean(blue)]
        return avg_color

    def check_color(self, max_depth):
        """
        Recursively checks if this cell's pixels are too varied, and subdivides it if necessary
        """
        pixels = self.sample_pixel_colors(25)
        pxl_stdev = np.mean([np.std([i[0] for i in pixels]),
                            np.std([i[1] for i in pixels]),
                            np.std([i[2] for i in pixels])])

        if pxl_stdev > 25 and not self.has_divided:
            self.subdivide()
    
        if self.has_divided and max_depth > 0:
            self.northeast.check_color(max_depth-1)
            self.northwest.check_color(max_depth-1)
            self.southwest.check_color(max_depth-1)
            self.southeast.check_color(max_depth-1)

        
if __name__ == '__main__':
    img_file = 'obi.png'
    img = Image.open('samples/' + img_file)

    fig, ax = plt.subplots(figsize=(7, 7))
    ax.imshow(img)

    rect = Rectangle((0, 0), img.width, img.height, facecolor='none')
    qt = Quadtree(rect, ax, img)
    qt.check_color(6)
    qt.draw()

    plt.axis('off')
    plt.savefig('out/compressed_' + img_file)
    plt.show()
    