import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle
from PIL import Image
import sys


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
        # int() truncates result, hex() converts back to hexadecimal, strip() and rjust() to match mcolors format
        avg_color = hex(int(np.mean(self.sample_pixel_colors(25)))).strip('0x').rjust(6, '0')
        self.boundary.set_facecolor(mcolors.to_rgb(f'#{avg_color}'))
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
        hex_pix = []

        # Store hex colors of uniformly sampled pixels in this quadrant
        x = int(self.boundary.get_x())
        y = int(self.boundary.get_y())
        w = int(self.boundary.get_width())
        h = int(self.boundary.get_height())
        for i in range(x, x+w, step):
            for j in range(y, y+h, step):
                hex_pix.append('0x%02x%02x%02x' % pix[i, j][0:3])  # Only use RGB values (ignore alpha)
        return [eval(i) for i in hex_pix]
            
    def check_color(self, max_depth):
        """
        Recursively checks if this cell's pixels are too varied, and subdivides it if necessary
        """
        pixels = self.sample_pixel_colors(25)
        if np.std(pixels) > 0x100000 and not self.has_divided:
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

    rect = Rectangle((0, 0), img.width, img.height, facecolor='none', edgecolor='k', linewidth=1)
    qt = Quadtree(rect, ax, img)
    qt.check_color(6)
    qt.draw()

    plt.axis('off')
    plt.savefig('out/compressed_' + img_file)
    plt.show()
    